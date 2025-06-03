mov s0, 0x8000;
mov v0, [s0+0]; 
mov s0, 0;
mov v1, s0, 0xFFFF;

vgt v2, v0, v1;
and v3, v0, v2;

mov s1, 0x8020;
mov [s1+0], v3;

halt;