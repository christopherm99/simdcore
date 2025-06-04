#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <string.h>
#include <signal.h>

#define ZF 0x01
#define SF 0x02
#define FLAG(x) (((x) == 0) ? ZF : 0) | ((x) & 0x8000 ? SF : 0)

struct instruction {
  uint8_t aluctrl:3;
  uint8_t opcode:5;
  uint8_t A;
  uint8_t B;
  uint8_t C;
};

typedef uint16_t vreg_t[8];

__attribute__((aligned(4096))) uint8_t memory[65536] = {0};
uint8_t flags = 0;
uint16_t pc = 0;
uint16_t sregs[256] = {0};
vreg_t vregs[256] = {0};
vreg_t vperm = {0};

uint16_t input_addr = 0x8000;
uint16_t second_input_addr = 0x8020;
uint16_t output_addr = 0x8040;

// for local testing purposes
void initialize_memory() {
  uint16_t values[8] = {2, 4, 6, 8, 10, 12, 14, 16};
  uint16_t second_values[8] = {0, 2, 4, 6, 8, 10, 12, 14};
  
  for (int i = 0; i < 8; i++) {
    memory[input_addr + i * 2] = values[i] >> 8;       
    memory[input_addr + i * 2 + 1] = values[i] & 0xFF; 
    
    memory[second_input_addr + i * 2] = second_values[i] >> 8;       
    memory[second_input_addr + i * 2 + 1] = second_values[i] & 0xFF; 
  }
}

uint8_t in() {
  uint8_t in;
  if (read(0, &in, 1) != 1) {
    if (errno != EAGAIN || errno != EWOULDBLOCK) {
      perror("read");
      exit(1);
    }
    flags = ZF;
    return 0;
  }
  flags = 0;
  return in;
}

void out(uint8_t out) {
  if (write(1, &out, 1) != 1) {
    perror("write");
    exit(1);
  }
}

void extract_indices(uint8_t arg1, uint8_t arg2, uint8_t arg3, int indices[8]) {
  uint32_t packed = (arg1 << 16) | (arg2 << 8) | arg3;
  for (int i = 0; i < 8; i++) {
    indices[i] = (packed >> (21 - (i * 3))) & 0x7;
  }
}

void dump() {
  fprintf(stderr, "PC: %04x\n", pc);
  for (int i = 0; i < 16; i++) fprintf(stderr, "s%d: 0x%04x\n", i, sregs[i]);
  for (int i = 0; i < 4; i++)
    fprintf(stderr, "v%d: %04x %04x %04x %04x %04x %04x %04x %04x\n",
        i, vregs[i][0], vregs[i][1], vregs[i][2], vregs[i][3], vregs[i][4], vregs[i][5], vregs[i][6], vregs[i][7]);
  for (int i = output_addr; i < 0x8060; i += 0x10)
    fprintf(stderr, "%04x: %02x%02x %02x%02x %02x%02x %02x%02x\n",
        i, memory[i], memory[i + 1], memory[i + 2], memory[i + 3], memory[i + 4], memory[i + 5], memory[i + 6], memory[i + 7]);
  fprintf(stderr, "vperm: %04x %04x %04x %04x %04x %04x %04x %04x\n",
      vperm[0], vperm[1], vperm[2], vperm[3], vperm[4], vperm[5], vperm[6], vperm[7]);
  exit(0);
}

void execute() {
  fprintf(stderr, "Starting execution...\n");

  while (1) {
    struct instruction inst = *((struct instruction *)(&memory[pc]));
    pc += 4;
    switch(inst.opcode) {
      case 0x00: // MOV
        switch (inst.aluctrl) {
          case 0: sregs[inst.A] = sregs[inst.B]; break;
          case 1: sregs[inst.A] = memory[sregs[inst.B] + inst.C] << 8 | memory[sregs[inst.B] + inst.C + 1]; break;
          case 2:
            memory[sregs[inst.A] + inst.B] = sregs[inst.C] >> 8;
            memory[sregs[inst.A] + inst.B + 1] = sregs[inst.C] & 0xFF;
            break;
          case 3: sregs[inst.A] = inst.B << 8 | inst.C; break;
          case 4: memcpy(&vregs[inst.A], &vregs[inst.B], sizeof(vreg_t)); break;
          case 5:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = memory[sregs[inst.B] + inst.C + i * 2] << 8 | memory[sregs[inst.B] + inst.C + i * 2 + 1];
            break;
          case 6:
            for (int i = 0; i < 8; i++) {
              memory[sregs[inst.A] + inst.B + i * 2] = vregs[inst.C][i] >> 8;
              memory[sregs[inst.A] + inst.B + i * 2 + 1] = vregs[inst.C][i] & 0xFF;
            }
            break;
          case 7:
            for (int i = 0; i < 8; i++)
              if (inst.C & (1 << i)) vregs[inst.A][i] = sregs[inst.B];
            break;
        } break;
      case 0x01: // SCALAR ALU
        switch (inst.aluctrl) {
          case 0: sregs[inst.A] = sregs[inst.B] + sregs[inst.C]; break;
          case 1: sregs[inst.A] = sregs[inst.B] * sregs[inst.C]; break;
          case 2: sregs[inst.A] = -sregs[inst.B]; break;
          case 3: sregs[inst.A] = sregs[inst.B] / sregs[inst.C]; break;
          case 4: sregs[inst.A] = sregs[inst.B] & sregs[inst.C]; break;
          case 5: sregs[inst.A] = sregs[inst.B] | sregs[inst.C]; break;
          case 6: sregs[inst.A] = sregs[inst.B] ^ sregs[inst.C]; break;
          case 7: sregs[inst.A] = ~sregs[inst.B]; break;
        } break;
      case 0x02: // VECTOR ALU
        switch (inst.aluctrl) {
          case 0:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = vregs[inst.B][i] + vregs[inst.C][i];
            break;
          case 1:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = vregs[inst.B][i] * vregs[inst.C][i];
            break;
          case 2:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = -vregs[inst.B][i];
            break;
          case 3:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = vregs[inst.B][i] / vregs[inst.C][i];
            break;
          case 4:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = vregs[inst.B][i] & vregs[inst.C][i];
            break;
          case 5:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = vregs[inst.B][i] | vregs[inst.C][i];
            break;
          case 6:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = vregs[inst.B][i] ^ vregs[inst.C][i];
            break;
          case 7:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = ~vregs[inst.B][i];
            break;
        } break;
      case 0x03: // VECTOR COMPARE & PERM OPS
        switch (inst.aluctrl) {
          case 0:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = ((int16_t)vregs[inst.B][i] == (int16_t)vregs[inst.C][i]) ? 0xFFFF : 0;
            break;
          case 1:
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = ((int16_t)vregs[inst.B][i] > (int16_t)vregs[inst.C][i]) ? 0xFFFF : 0;
            break;
          case 2: { // SCATTER
            int indices[8];
            extract_indices(inst.A, inst.B, inst.C, indices);
            uint16_t temp[8] = {0};
            for (int i = 0; i < 8; i++) {
              temp[indices[i]] = vperm[i];
            }
            for (int i = 0; i < 8; i++) {
                vperm[i] = temp[i];
            }
            break;
          }
          case 3: { // GATHER
            int indices[8];
            extract_indices(inst.A, inst.B, inst.C, indices);
            uint16_t temp[8];
            for (int i = 0; i < 8; i++) {
              temp[i] = vperm[indices[i]];
            }
            for (int i = 0; i < 8; i++) {
                vperm[i] = temp[i];
            }
            break;
          }
          case 4: // LOAD
            for (int i = 0; i < 8; i++) vperm[i] = vregs[inst.A][i];
            break;
          case 5: // STORE
            for (int i = 0; i < 8; i++) vregs[inst.A][i] = vperm[i];
            break;
          default: fprintf(stderr, "unknown vector compare instruction\n"); exit(1);
        } break;
      case 0x04: // JUMP
        switch (inst.aluctrl) {
          case 0: pc = inst.A << 8 | inst.B; continue;
          case 1: if (flags & ZF) pc = inst.A << 8 | inst.B; continue;
          case 2: if (!(flags & ZF)) pc = inst.A << 8 | inst.B; continue;
          case 3: if (!(flags & SF) || flags & ZF) pc = inst.A << 8 | inst.B; continue;
          case 4: if (flags & SF || flags & ZF) pc = inst.A << 8 | inst.B; continue;
          case 5: if (!(flags & SF) && !(flags & ZF)) pc = inst.A << 8 | inst.B; continue;
          case 6: if (flags & SF) pc = inst.A << 8 | inst.B; continue;
          case 7: pc = sregs[inst.A]; continue;
        } break;
      case 0x05: // TEST
        switch (inst.aluctrl) {
          case 0: flags = FLAG(sregs[inst.A] - sregs[inst.B]); break;
          case 1: flags = FLAG(sregs[inst.A] - (inst.B << 8 | inst.C)); break;
          case 2: flags = FLAG((inst.A << 8 | inst.B) - sregs[inst.C]); break;
          case 3: flags = inst.A & (ZF | SF); break;
          default: fprintf(stderr, "unknown test instruction\n"); exit(1);
        } break;
      case 0x06: // IO
        switch (inst.aluctrl) {
          case 0: sregs[inst.A] = (sregs[inst.A] & 0xFF00) | in(); break;
          case 1: sregs[inst.A] = (sregs[inst.A] & 0x00FF) | (in() << 8); break;
          case 2: out(sregs[inst.A] & 0xFF); break;
          case 3: out(sregs[inst.A] >> 8); break;
          default: fprintf(stderr, "unknown IO instruction\n"); exit(1);
        } break;
      case 0x07: return;
      default: fprintf(stderr, "unknown opcode 0x%02x\n", inst.opcode); exit(1);
    }
  }
}

int main(int argc, char **argv) {
  int fd;
  struct stat sb;

  if (fcntl(0, F_SETFL, O_NONBLOCK) == -1) {
    perror("fcntl");
    exit(1);
  }

  if (argc < 2) {
    fprintf(stderr, "usage: %s <input_file>\n", argv[0]);
    exit(1);
  }

  if ((fd = open(argv[1], O_RDONLY)) == -1) {
    perror("open");
    exit(1);
  }

  if (fstat(fd, &sb) == -1) {
    perror("fstat");
    exit(1);
  }

  if (read(fd, memory, sb.st_size) != sb.st_size) {
    perror("read");
    exit(1);
  }

  close(fd);

  // comment this out to use test.py instead
  initialize_memory();

  // add HLT (0x07) instruction at the end of the memory
  memcpy(&memory[sb.st_size], &(struct instruction){0, 0x07, 0, 0, 0}, sizeof(struct instruction));

  signal(SIGINT, dump);

  execute();

  // write mem back to bin file
  if ((fd = open(argv[1], O_WRONLY)) != -1) {
      write(fd, memory, 65536);
      close(fd);
  }

  fprintf(stderr, "Execution finished.\n");
  dump();


  return 0;
}
