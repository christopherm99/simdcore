mov s0, 0x0;
mov v0, [s0+0]; 

mov vperm, v0;
gather 0, 4, 1, 5, 2, 6, 3, 7;
mov v2, vperm;

mov s0, 0x80;
mov [s0+0], v2;