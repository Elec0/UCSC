;#!/afs/cats.ucsc.edu/courses/cmps112-wm/usr/racket/bin/mzscheme -qr
;#!/usr/bin/racket
#lang racket

;; $Id: sbi.scm,v 1.3 2016-09-23 18:23:20-07 - - $
;;
;; NAME
;;    sbi.scm - silly basic interpreter
;;
;; SYNOPSIS
;;    sbi.scm filename.sbir
;;
;; DESCRIPTION
;;    The file mentioned in argv[1] is read and assumed to be an SBIR
;;    program, which is the executed.  Currently it is only printed.
;;

(define *stderr* (current-error-port))


; Define the hash tables we need
(define *function-table* (make-hash))
(define *label-table* (make-hash))
(define *variable-table* (make-hash))

; Function table imperatives
(define (function-get key)
        (hash-ref *function-table* key))
(define (function-put! key value)
        (hash-set! *function-table* key value))
; Label table imperatives
(define (label-get key)
        (hash-ref *label-table* key))
(define (label-put! key value)
        (hash-set! *label-table* key value))
; Label table imperatives
(define (variable-get key)
        (hash-ref *variable-table* key))
(define (variable-put! key value)
        (hash-set! *variable-table* key value))

; *** BASIC functions definitions ***

; Print out 
(define (basic-print msg)
	(printf "basic-print: ~s~n" msg)
	(when (not (null? (car msg)))
		(begin 
			(if (string? (car msg))
				(begin (display (car msg))(newline) )
				; Else, eval the non-string
				(begin (display (eval (car msg))(newline)) )
			)
			(when (not (null? cdr msg)) ; There's still things to print
				(basic-print (cdr msg))
			)
		)
	)
  
)

; Jump to a different point in the program
(define (basic-goto label program)
	(if (null? label)
		(err-syntax #:msg "goto expects 1 argument.~n")
		(run-program program (- (label-get label) 1))
	)
)

(define (basic-dim)
	(void)
)

(define (basic-let)
	(void)
)

; *** End BASIC functions ***


; *** Error functions ***

; Generic syntax error
; Usage: (err-syntax) or (err-syntax #:msg "Message here")
(define (err-syntax #:msg [message "Generic error"])
	(printf "Syntax error: ~s~n" message)
	(quit)
)

; *** End error functions ***


; Initialize all the functions we allow the BASIC program to have, at the start
(for-each
    (lambda (pair)
            (function-put! (car pair) (cadr pair)))
    `(
        (log10_2 0.301029995663981195213738894724493026768189881)
        (sqrt_2  1.414213562373095048801688724209698078569671875)
        (e       2.718281828459045235360287471352662497757247093)
        (pi      3.141592653589793238462643383279502884197169399)
        (div     ,(lambda (x y) (floor (/ x y))))
        (log10   ,(lambda (x) (/ (log x) (log 10.0))))
        (mod     ,(lambda (x y) (- x (* ((function-get 'div) x y) y))))
        (quot    ,(lambda (x y) (truncate (/ x y))))
        (rem     ,(lambda (x y) (- x (* ((function-get 'quot) x y) y))))
        (+       ,+)
        (-		 ,-)
        (^       ,expt)
        (ceil    ,ceiling)
        (exp     ,exp)
        (floor   ,floor)
        (log     ,log)
        (sqrt    ,sqrt)
        (print   ,basic-print)
        (goto	 ,basic-goto)
        (dim	 ,basic-dim)
        (let	 ,basic-let)
        

     ))

; Initialize the variable table
(for-each
     (lambda (pair)
          (variable-put! (car pair) (cadr pair)))
     `(
        (e       2.718281828459045235360287471352662497757247093)
        (pi      3.141592653589793238462643383279502884197169399)
      )
)


; The name of the file (sbi.scm)
(define *run-file*
    (let-values
        (((dirpath basepath root?)
            (split-path (find-system-path 'run-file))))
        (path->string basepath))
)


; Print out every item in a list?
(define (die list)
    (for-each (lambda (item) (display item *stderr*)) list)
    (newline *stderr*)
    (exit 1)
)

; Display how to properly use the program
(define (usage-exit)
    (die `("Usage: " ,*run-file* " filename"))
)

(define (quit)
	(newline)(die `("Program ending..."))
)

; I believe this is reading the program from a file
(define (readlist-from-inputfile filename)
    (let ((inputfile (open-input-file filename))) ; Looping through the file? Or maybe it reads it in one read
         (if (not (input-port? inputfile)) ; Make sure it's able to be opened
             (die `(,*run-file* ": " ,filename ": open failed"))
             (let ((program (read inputfile))) ; This does the actual reading? It looks like a loop but I'm not sure
                  (close-input-port inputfile) ; When we're done, close the file
                         program) ; Return the result?
          )))

; Define a function to write a program line by line
(define (write-program-by-line filename program)
    (printf "==================================================~n")
    (printf "~a: ~s~n" *run-file* filename)
    (printf "==================================================~n")
    (printf "(~n")
    (map (lambda (line) (printf "~s~n" line)) program)
    (printf ")~n"))

; The function evalexpr outlines how to evaluate a list recursively.
(define (evalexpr expr)
   (cond ((number? expr) expr)
         ((symbol? expr) (hash-ref *function-table* expr #f))
         ((pair? expr)   (apply (hash-ref *function-table* (car expr))
                                (map evalexpr (cdr expr))))
         (else #f))
)

; Run through and do all the stuff for the labels
(define (eval-labels program)
	(when (not (null? program))
		(let ((1st (first program))) ; Get the first current line of the program
		
			(when (not (null? (cdr 1st))) ; Make sure there are things in the cdr
				
				(when (symbol? (cadr 1st)); Does the line have a label?
					(label-put! (cadr 1st) (+ (car 1st) 1))
				)	
			)
		)
		(eval-labels (cdr program)) ; Recurse with the rest of the program
	)
)


; Do the actual executing of the line
(define (exec-line command program line-num)
	(if (hash-has-key? *function-table* (car command))
		(begin ; We need some special cases for some commands
		
			(cond 
				[(eqv? 'goto (car command)) ; Goto needs the entire program to be able to pass it back into run-program with a different line number
					((function-get (car command)) (cadr command) program)]
				
				[else ((function-get (car command)) (cdr command))]
			)
		)
		(begin 
			(printf "Syntax error: ~s is not a command.~n" (car command))
			(quit)
		)
	)
)

; Go through every line and parse the command out, then call exec-line
(define (run-program program line-num)
	(when (>= (length program) line-num) ; Make sure we haven't run out of program to execute
		
		(let ((line (list-ref program (- line-num 1)))) ; Get the element at line-num and parse it
			; Parse and run the line
			; The line number and label don't matter, the only thing that matters is the statement
			
			(when (> (length line) 1) ; Check for just a line number

				(begin ; There is more than just a line number

					(when (equal? (length line) 2) ; If the line has 2 parts, which means there's 2 options for format

						(when (pair? (second line)) ; If line # + cmd
							(exec-line (second line) program line-num) ; Execute line

							; Else, line # + label, so ignore
						)
					)
					(when (equal? (length line) 3) ; The line has 3 parts, which is line # + label + command
						(exec-line (third line) program line-num)
					)
				)
			)
		)
		
		(run-program program (+ line-num 1)) ; Recurse with the next line
	)
	(quit)
)

; Where we do our actual new stuff
; program is the actual program we read in from the file
(define (eval-program program)
	(eval-labels program)
	(run-program program 1)
	
)


; Define the main function
(define (main arglist)
    (if (or (null? arglist) (not (null? (cdr arglist)))) ; If the arglist is null, or the cdr of the arglist is null, display how to use the program
        (usage-exit)
        (let* ((sbprogfile (car arglist)) ; Else, 
              (program (readlist-from-inputfile sbprogfile)))
              (write-program-by-line sbprogfile program)
              (eval-program program)
        )
	)
)


; The actual code to run first
(main (vector->list (current-command-line-arguments)))


; *** REFERENCE CODE ***
; How to call a function in the table
;((function-get 'print) "test")

; Loop over a hashtable
;(hash-for-each *label-table* (lambda (key value) (printf "~s = ~s~n" key value)))
; OR, (printf "~s" *label-table*)
