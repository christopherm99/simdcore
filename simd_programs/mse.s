mov s0, 0x8000;
mov v0, [s0+0]; 
mov v1, [s0+0x20]; 

neg v5, v1; 
add v2, v0, v5;
mul v2, v2, v2;

mov vperm, v2;
gather 4, 5, 6, 7, 0, 1, 2, 3;
mov v4, vperm;
add v2, v2, v4;

mov vperm, v2;
gather 2, 3, 0, 1, 2, 3, 0, 1;
mov v4, vperm;
add v2, v2, v4;

mov vperm, v2;
gather 1, 0, 1, 0, 1, 0, 1, 0;
mov v4, vperm;
add v2, v2, v4;

mov s5, 8;
mov v10, s5;
div v9, v2, v10;

mov s5, 0x8040;
mov [s5+0], v9;

halt;