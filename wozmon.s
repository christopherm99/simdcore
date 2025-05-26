mov s5, 0x80; ;nop

LOOP:
  ;mov s0, 0;
  inh s0;
  inl s0;
  test s0, 0x52; ;type 52 to READ MEM (i.e. '5200')
  jeq READ ;
  test s0, 0x56; ;type 56 to READ VEC MEM (i.e. '5600')
  jeq READ_V ;
  test s0, 0x57 ;type 57 to WRITE MEM (i.e. '570011')
  jeq WRITE ;
  test s0, 0x58 ;type 58 to RUN PROG (i.e. '5850')
  jeq RUN ;
  j LOOP ; 

READ:
  inh s2;
  inl s2;
  mov s3, [s2+0];
  outh s3;
  outl s3;
  j LOOP ;

WRITE:
  inh s0;
  inl s0;
  inh s1;
  inl s1;
  mov [s0+0], s1;
  ;outh s1;
  outl s1; ;output what was written to MEM 
  j LOOP ;

RUN:
  inh s0;
  inl s0;
  jr s0;

READ_V:
  inh s2;
  inl s2;
  mov s3, [s2+0];
  mov s4, [s2+2];
  mov s5, [s2+4];
  mov s6, [s2+6];
  mov s7, [s2+8];
  mov s8, [s2+10];
  mov s9, [s2+12];
  mov s10, [s2+14];
  outh s3;
  outl s3;
  outh s4;
  outl s4;
  outh s5;
  outl s5;
  outh s6;
  outl s6;
  outh s7;
  outl s7;
  outh s8;
  outl s8;
  outh s9;
  outl s9;
  outh s10;
  outl s10;
  j LOOP ;

  