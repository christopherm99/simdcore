mov s0, 0;    ; s0 <- 0
mov s1, 10;   ; s1 <- 10
mov s2, 5;    ; s2 <- 5
mov s3, 0;    ; s3 <- 0
mov s4, 1;    ; s4 <- 1

LOOP:
    test s0, s1 ; cmp s0 - s1 
    jge END ; if s0 >= s1, jump to END 

    test s0, s2 ; cmp s0 - s1
    jne SKIP ; if s0 != s2, jump to SKIP

    mov s3, 100 ; only executed when s0 == s2
    j   NEXT ; unconditional jump to NEXT
SKIP:
    mov s3, 200 ; only executed when s0 != s2
NEXT:
    add s0, s0, s4 ; s0 <- s0 + s4 (1)
    j   LOOP ; unconditional jump back to start of loop
END:
    mov s5, s3;
