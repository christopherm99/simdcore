;; transpose.s - transpose flattened matrix
START:
  mov s30, 0x3e20 ; "> "
  outh s30 ;
  outl s30 ;
  mov s0, 0x8000 ; buffer address
  mov s1, 0 ; input byte
READC:
  inl s1 ;
  jeq READC ; wait for input
  mov [s0 + 0], s1 ;
  mov s30, 2 ;
  add s0, s0, s30 ;
  cmp s1, 0xa ; newline
  jeq GO ;
  j READC ;
GO:
  mov s1, 0x8000 ;
  mov v0, [s1 + 0] ;
  mov vperm, v0;
  gather 0, 4, 1, 5, 2, 6, 3, 7;
  mov v2, vperm;

  mov s0, 0x8040;
  mov [s0+0], v2;
  mov s3, 0 ; byte counter
OUT:
  mov s2, [s1 + 0x40] ;
  cmp s2, 0 ;
  jeq SKIP_OUTPUT ;
  outl s2 ;
SKIP_OUTPUT:
  mov s2, 1 ;
  add s1, s1, s2 ;
  add s3, s3, s2 ;
  cmp s3, 16 ;
  jne OUT ;
  mov s4, 0xa ;
  outl s4 ;
  j START ;