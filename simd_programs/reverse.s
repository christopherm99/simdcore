mov s0, 0x8000;
mov v0, [s0+0]; 

mov vperm, v0;
scatter 7, 6, 5, 4, 3, 2, 1, 0;
mov v2, vperm;

mov s0, 0x8020;
mov [s0+0], v2;
halt;