mov s0, 0x8000;
mov v0, [s0+0];
mov v1, [s0+0x20];

add v2, v0, v1;
mov s0, 0x8040;
mov [s0+0], v2;
halt;