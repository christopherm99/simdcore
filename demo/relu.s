.org 0x5000
START:
  mov s30, 0x3e20 ;
  outh s30 ;
  outl s30 ;
  mov s0, 0x8000 ;
  mov s1, 0 ;
READC:
  inl s1 ;
  jeq READC ;
  mov [s0 + 0], s1 ;
  mov s30, 2 ;
  add s0, s0, s30 ;
  cmp s1, 0xa ;
  jeq GO ;
  j READC ;
GO:
  mov s0, 0x8000 ;
  mov v0, [s0+0] ;
  mov s2, 0x30 ;
  mov v3, s2 ;
  neg v3, v3 ;
  add v0, v0, v3 ;
  mov s0, 0 ;
  mov v1, s0 ;
  vgt v2, v0, v1 ;
  and v3, v0, v2 ;
  mov s1, 0x8040 ;
  mov [s1+0], v3 ;
  mov s1, 0x8040 ;
  mov s20, 0 ;
OUTPUT_LOOP:
  mov s2, [s1 + 0] ;
  mov s3, s2 ;
  mov s4, 10 ;
  mov s6, 0 ;
TENS_LOOP:
  cmp s3, s4 ;
  jlt TENS_DONE ;
  neg s7, s4 ;
  add s3, s3, s7 ;
  mov s7, 1 ;
  add s6, s6, s7 ;
  j TENS_LOOP ;
TENS_DONE:
  mov s4, 0x30 ;
  cmp s6, 0 ;
  jeq SKIP_TENS ;
  add s6, s6, s4 ;
  outl s6 ;
SKIP_TENS:
  add s3, s3, s4 ;
  outl s3 ;
  mov s5, 0x20 ;
  outl s5 ;
SKIP_ELEMENT:
  mov s2, 2 ;
  add s1, s1, s2 ;
  mov s2, 1 ;
  add s20, s20, s2 ;
  cmp s20, 8 ;
  jne OUTPUT_LOOP ;
  mov s4, 0xa ;
  outl s4 ;
  j START ;