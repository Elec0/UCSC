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

	BTN4:		000000000000 0000 0011 0000
	BTN3:		000000000000 0000 0101 0000
	BTN2:		000000000000 0000 1001 0000
     
	BTN1 (F):	000000000000 0000 0110 1110
	~BTN1:		000000000000 0000 0110 1100
    */
    
    /* your code goes underneath this */
    LA $a0, Greeting
    JAL puts
    NOP
    
loop:
    /* I guess it's probably easier to use PORTESET, but I couldn't
     * wrap my mind around how to use it correctly. I'll work on that.
    */
    LW $t2, PORTD
    LW $t3, PORTF
    LA $t5, PORTE
    
    ANDI $t9, $t9, 0x0	    # Clear
    ADDI $t9, $t9, 0x0FF    # Set to 1111 1111
    SW $t9, TRISECLR	    # Clear all LEDs in TRISE
    SW $t9, PORTECLR	    # Same for PORTE
    
    # Switches to LEDs
    SRL $t1, $t2, 8	    # Shift PORTD 8 bits to right
    ANDI $t6, $t1, 0b1111   # AND that with the bits of all the switches on
    SW $t6, 0($t5)	    # Write that AND to PORTE's first 4 bits E0-E3 (LEDs)
    
    # Buttons on D to LEDs
    SRL $t1, $t2, 5	    # Shift the bits over to the buttons part
    ANDI $t6, $t1, 0b111    # AND with the 3 bits for buttons
    SLL $t6, $t6, 5	    # We want to light up LEDs E5-E7, so shift 5 over
    SW $t6, 0($t5)
    
    # Button on F to LEDs
    SRL $t1, $t3, 1	    # Shift 1 over on F
    ANDI $t6, $t1, 0b1	    # AND with 1, since only 1 bit
    SLL $t6, $t6, 4	    # Shift back over
    SW $t6, 0($t5)	    # Store back into PORTE
    
    B loop
    NOP
	
endProgram:    J endProgram
    NOP
.end main



.data
Greeting:   .asciiz "LED Control Program\n"


