mov s0, 0; ; i=0
mov s1, 8; ; m=8
mov s31, 8; ; n=8
mov s2, 1; ; increment

OUTER_LOOP:
    cmp s0, s1;
    jge END ;

    ; LOAD a row of A
    mov s4, 0x8000;
    mov s5, 16;
    mul s6, s5, s0; ; i*16 (assuming 8 elements)
    add s25, s4, s6; row = base_addr + i*16
    mov v0, [s25+0];

    mov s3, 0; ; j=0
    
    INNER_LOOP:
        cmp s3, s31;
        jge NEXT ; 
        
        ; LOAD a column of B
        mov s7, 0x8200; ; base
        mov s8, 2; 
        mul s9, s3, s8; ; j * 2
        add s7, s7, s9; ; base_addr + j*2 (get column)
        add s10, s7, s9; ; (base_addr + j*2) + j*2 (get elements in column) 

        mov s11, [s7+0]; ;
        mov s12, [s7+16];
        mov s13, [s7+32];
        mov s14, [s7+48];
        mov s15, [s7+64];
        mov s16, [s7+80];
        mov s17, [s7+96];
        mov s18, [s7+112];

        mov v1, s11, 0x01;
        mov v1, s12, 0x02;
        mov v1, s13, 0x04;
        mov v1, s14, 0x08;
        mov v1, s15, 0x10;
        mov v1, s16, 0x20;
        mov v1, s17, 0x40;
        mov v1, s18, 0x80;

        ; Compute inner product
        mul v2, v0, v1;

        mov vperm, v2;
        gather 4, 5, 6, 7, 0, 1, 2, 3;
        mov v3, vperm;
        add v2, v2, v3;

        mov vperm, v2;
        gather 2, 3, 0, 1, 2, 3, 0, 1;
        mov v3, vperm;
        add v2, v2, v3;
        
        mov vperm, v2;
        gather 1, 0, 1, 0, 1, 0, 1, 0;
        mov v3, vperm;
        add v2, v2, v3;

        ; scratchpad to extract single element from vector
        mov s16, 0x8800;
        mov [s16+0], v2;
        mov s17, [s16+0];

        ; s17 contains C[i][j]
        mov s16, 0x8400;   ; base address for C matrix
        mov s19, 16;      ; row size (8 elements * 2 bytes each)
        mul s18, s0, s19; ; i * 16 (no adjustment needed now)
        mov s20, 2;       ; element size
        mul s21, s3, s20; ; j * 2
        add s18, s18, s21; ; i*16 + j*2
        add s22, s16, s18; ; base_addr + i*16 + j*2
        mov [s22+0], s17;
        
        add s3, s3, s2; ; j++
        j INNER_LOOP ; 

    NEXT:
        add s0, s0, s2; ; i++
        j OUTER_LOOP ;
            
END:
halt;