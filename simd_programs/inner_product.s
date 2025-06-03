mov s0, 0x8000;
mov v0, [s0+0];
mov v1, [s0+0x20];
mul v2, v0, v1;

mov vperm, v2;
gather 0, 1, 2, 3, 4, 5, 6, 7;
mov v3, vperm;
mov vperm, v2;
gather 4, 5, 6, 7, 0, 1, 2, 3;
mov v4, vperm;
add v2, v3, v4;

mov vperm, v2;
gather 0, 1, 2, 3, 0, 1, 2, 3;
mov v3, vperm;
mov vperm, v2;
gather 2, 3, 0, 1, 2, 3, 0, 1;
mov v4, vperm;
add v2, v3, v4;

mov vperm, v2;
gather 0, 1, 0, 1, 0, 1, 0, 1;
mov v3, vperm;
mov vperm, v2;
gather 1, 0, 1, 0, 1, 0, 1, 0;
mov v4, vperm;
add v2, v3, v4;

mov s1, 0x8040;
mov [s1+0], v2;
halt;