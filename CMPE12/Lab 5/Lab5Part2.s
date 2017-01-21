/* Name: Aaron Steele
   Class: CMPE 12L
   Date: 11/14/2016
*/
#include <WProgram.h>
#include <xc.h>
/* define all global symbols here */
.global main
    

.text
.set noreorder

.ent main
main:
    /* this code blocks sets up the ability to print, do not alter it */
    ADDIU $v0,$zero,1
    LA $t0,__XC_UART
    SW $v0,0($t0)
    LA $t0,U1MODE
    LW $v0,0($t0)
    ORI $v0,$v0,0b1000
    SW $v0,0($t0)
    LA $t0,U1BRG
    ADDIU $v0,$zero,12
    SW $v0,0($t0)
    
    /* Input maps
     * LEDs: E0-E7
     * Buttons: BTN1:F1, BTN2:D5, BTN3:D6, BTN4:D7
     * Switches: SW1:D8, SW2:D9, SW3:D10, SW4:D11
     
	Nothing (D):	000000000000 0000 0001 0000
	SW1:		000000000000 0001 0001 0000
	SW2:		000000000000 0011 0001 0000
	SW3:		000000000000 0111 0001 0000
	SW4:		000000000000 1111 0001 0000
    */
    
    /* your code goes underneath this */
    LA $a0, Greeting
    JAL puts
    NOP
    
    LI $t0, 0b01
    LI $t1, 1	# Shift direction. 1 = right, 0 = left
    LI $t8, 1	# Delay multiplier
    
loop:
    LW $t2, PORTD
    LA $t5, PORTE
    
    ANDI $t9, $t9, 0x0	    # Clear
    ADDI $t9, $t9, 0x0FF    # Set to 1111 1111
    SW $t9, TRISECLR	    # Clear all LEDs in TRISE
    SW $t9, PORTECLR	    # Same for PORTE
    
    # Read switches
    SRL $t2, $t2, 8	    # Shift switch bits
    ANDI $t8, $t2, 0b1111   # Extract shift bits and assign to multiplier
    ADDI $t8, $t8, 1	    # Range for multiplier is 1-16, not 0-15.
    
    SW $t0, 0($t5) # Light up proper LED
    
    AND $a0, $a0, 0
    LI $t6, 100		    # Delay base time
    MULT $t6, $t8	    # Delay base * multiplier
    MFLO $a0		    # Get result, put into a0
    JAL mydelay		    # Delay
    NOP
    
    SW $zero, 0($t5) # Turn off LED
    
    BGT $t0, 0b1000000, flipShift # If greater than max LED value, shift other way
    NOP
    
cont:
    BEQ $t1, 1, shiftLeft # Figure out which way we're shifting
    NOP
    B shiftRight
    NOP
    
shiftLeft:
    SLL $t0, $t0, 1
    B loop
    NOP
shiftRight:
    SRL $t0, $t0, 1
    BEQZ $t0, flipShiftRight # If we've shifted to 0, flip the shift
    NOP
    B loop
    NOP
    
    
flipShift:
    BEQ $t1, 1, flipShiftLeft
    NOP
    BEQ $t1, 0, flipShiftRight
    NOP
flipShiftRight: # Flip shift to right
    ADD $t1, $t1, 1 # Make shift 1
    LI $t0, 0b01    # Because it's 0, and we need it to be 1
    B cont
    NOP
flipShiftLeft: # Flip shift to left
    ADD $t1, $t1, -1 # Make shift 0
    B cont	    
    NOP
	
endProgram:    J endProgram
    NOP
    
    /* Loop $a0 times to waste time */
mydelay:
    MOVE $s0, $a0 # Copy a0 into s0
delayLoop:
    BEQ $s0, $zero, delayEnd
    NOP
    ADDI $s0, $s0, -1
    
    B delayLoop
    NOP
delayEnd:    
    JR $ra
    NOP
.end main



.data
Greeting:   .asciiz "LED Control Program\n"
printDec:    .asciiz "%d "
fin:	    .asciiz "Done.\n"


