#include <unistd.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>

int main(int argc, char **argv) {
  int inputs = argc - 1;
  int *fds;
  char *eof;

  if (inputs < 1) {
    fprintf(stderr, "usage: %s [INPUT_FILES]...\n", argv[0]);
    return 1;
  }

  if ((fds = malloc(inputs * sizeof(int))) == NULL || (eof = calloc(inputs, sizeof(char))) == NULL) {
    fprintf(stderr, "buy more ram loser\n");
    return 1;
  }

  for (int i = 0; i < inputs; i++) {
    if ((fds[i] = open(argv[i + 1], O_RDONLY)) == -1) {
      perror("open");
      return 1;
    }
  }

  while (1) {
    uint32_t out = 0;
    char all_eof = 1;

    for (int i = 0; i < inputs; i++) {
      uint32_t in;
      ssize_t amt;
      if (eof[i]) continue;
      if ((amt = read(fds[i], &in, 4)) == 0) {
        eof[i] = 1;
        continue;
      } else if (amt == -1) {
        perror("read");
        return 1;
      } else if (amt != 4) {
        fprintf(stderr, "read %zd bytes from file %s, expected 4\n", amt, argv[i + 1]);
        return 1;
      }
      if (out != 0 && in != 0) fprintf(stderr, "warning: linking collsion detected\n");
      out |= in;
      all_eof = 0;
    }
    write(1, &out, 4);
    if (all_eof) break;
  }

  return 0;
}
