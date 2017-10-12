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
(define (basic-print msg)
  (if (not (null? msg))
      (begin (display msg) (newline))
      (display "Error: Message is null.")
      )
  
)

; *** End BASIC functions ***

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
        (^       ,expt)
        (ceil    ,ceiling)
        (exp     ,exp)
        (floor   ,floor)
        (log     ,log)
        (sqrt    ,sqrt)
        (print   ,basic-print)

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

; Where we do our actual new stuff
; program-text is the actual program we read in from the file. 
(define (eval-program program-text)
  ((function-get `print) "Test print")
  
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
