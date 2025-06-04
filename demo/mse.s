.org 0x4000
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
  jeq START2 ;
  j READC ;
START2:
  mov s30, 0x3e20 ;
  outh s30 ;
  outl s30 ;
  mov s0, 0x8020 ;
  mov s1, 0 ;
READC_2:
  inl s1 ;
  jeq READC_2 ;
  mov [s0 + 0], s1 ;
  mov s30, 2 ;
  add s0, s0, s30 ;
  cmp s1, 0xa ;
  jeq GO ;
  j READC_2 ;
GO:
  mov s0, 0x8000 ;
  mov v0, [s0+0] ;
  mov v1, [s0+0x20] ;
  mov s2, 0x30 ;
  mov v5, s2 ;
  neg v5, v5 ;
  add v0, v0, v5 ;
  add v1, v1, v5 ;
  neg v5, v1 ;
  add v2, v0, v5 ;
  mul v2, v2, v2 ;
  mov vperm, v2 ;
  gather 4, 5, 6, 7, 0, 1, 2, 3 ;
  mov v4, vperm ;
  add v2, v2, v4 ;
  mov vperm, v2 ;
  gather 2, 3, 0, 1, 2, 3, 0, 1 ;
  mov v4, vperm ;
  add v2, v2, v4 ;
  mov vperm, v2 ;
  gather 1, 0, 1, 0, 1, 0, 1, 0 ;
  mov v4, vperm ;
  add v2, v2, v4 ;
  mov s5, 8 ;
  mov v10, s5 ;
  div v9, v2, v10 ;
  mov s1, 0x8040 ;
  mov [s1+0], v9 ;
  mov s2, [s1 + 0] ;
  mov s3, s2 ;
  mov s4, 100 ;
  mov s5, 0 ;
HUNDREDS_LOOP:
  cmp s3, s4 ;
  jlt HUNDREDS_DONE ;
  neg s7, s4 ;
  add s3, s3, s7 ;
  mov s6, 1 ;
  add s5, s5, s6 ;
  j HUNDREDS_LOOP ;
HUNDREDS_DONE:
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
  cmp s5, 0 ;
  jeq SKIP_HUNDREDS ;
  add s5, s5, s4 ;
  outl s5 ;
SKIP_HUNDREDS:
  cmp s5, s4 ;
  jgt OUTPUT_TENS ;
  cmp s6, 0 ;
  jeq SKIP_TENS ;
OUTPUT_TENS:
  add s6, s6, s4 ;
  outl s6 ;
SKIP_TENS:
  add s3, s3, s4 ;
  outl s3 ;
  mov s4, 0xa ;
  outl s4 ;
  j START ;