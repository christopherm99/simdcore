mov s0, 0;
mov s1, 10;
mov s2, 20;
mov s3, 30;
mov s4, 40;
mov s5, 50;
mov s6, 60;
mov s7, 70;

mov v0, s0, 0x01;        
mov v0, s1, 0x02;        
mov v0, s2, 0x04;        
mov v0, s3, 0x08;        
mov v0, s4, 0x10;        
mov v0, s5, 0x20;        
mov v0, s6, 0x40;        
mov v0, s7, 0x80;

mov v1, s0, 0x01;        
mov v1, s1, 0x02;        
mov v1, s2, 0x04;        
mov v1, s3, 0x08;        
mov v1, s4, 0x10;        
mov v1, s5, 0x20;        
mov v1, s6, 0x40;        
mov v1, s7, 0x80;

mul v2, v0, v1;   