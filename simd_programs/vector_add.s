mov s0, 0x0;
mov v0, [s0+0];
mov v1, [s0+32]; 

add v2, v0, v1;

mov s0, 0x80;
mov [s0+0], v2;

