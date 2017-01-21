.ORIG x3000

AND R0, R0, 0 ; Val
AND R1, R1, 0 ; 1s counter
AND R2, R2, 0 ; Loop counter
AND R3, R3, 0 ; Max bits
AND R4, R4, 0 ; Bit mask

LD R0, Val ; Load variables from labels
LD R3, Max 
LD R4, Mask

NOT R3, R3
ADD R3, R3, 1 ; 2SC R3


Loop
	ADD R5, R1, R3 ; Check if we've looped through all bits
	BRz Fin
	AND R5, R0, R4 ; AND the val with the mask
	BRn Count1		; If its 1 branch and count
	ADD R0, R0, R0 ; Left shift bits
	ADD R1, R1, 1 ; Increment loop counter
	BR Loop

Count1 ; We have a 1, so increment 1s counter
	ADD R1, R1, 1
	ADD R2, R2, 1 ; Increment loop counter
	ADD R0, R0, R0 ; Left shift bits
	BR Loop

Fin
	LD R5, AOff ; Convert into ascii
	ADD R2, R2, R5
	ADD R0, R2, 0
	OUT
END
HALT

AOff .FILL 	48
Max .FILL	16 ; Max 16 bits
Val .FILL 	b0001001101110000 ; The number of 1s to count goes in this value
Mask .FILL 	b1000000000000000
.END