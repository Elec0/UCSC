#ifndef __LIB_KERNEL_pqueue_H
#define __LIB_KERNEL_pqueue_H

/* Doubly linked list.

   This implementation of a doubly linked list does not require
   use of dynamically allocated memory.  Instead, each structure
   that is a potential list element must embed a struct pqueue_elem
   member.  All of the list functions operate on these `struct
   pqueue_elem's.  The pqueue_entry macro allows conversion from a
   struct pqueue_elem back to a structure object that contains it.

   For example, suppose there is a needed for a list of `struct
   foo'.  `struct foo' should contain a `struct pqueue_elem'
   member, like so:

      struct foo
        {
          struct pqueue_elem elem;
          int bar;
          ...other members...
        };

   Then a list of `struct foo' can be be declared and initialized
   like so:

      struct pqueue foo_list;

      pqueue_init (&foo_list);

   Iteration is a typical situation where it is necessary to
   convert from a struct pqueue_elem back to its enclosing
   structure.  Here's an example using foo_list:

      struct pqueue_elem *e;

      for (e = pqueue_begin (&foo_list); e != pqueue_end (&foo_list);
           e = pqueue_next (e))
        {
          struct foo *f = pqueue_entry (e, struct foo, elem);
          ...do something with f...
        }

   You can find real examples of list usage throughout the
   source; for example, malloc.c, palloc.c, and thread.c in the
   threads directory all use lists.

   The interface for this list is inspired by the list<> template
   in the C++ STL.  If you're familiar with list<>, you should
   find this easy to use.  However, it should be emphasized that
   these lists do *no* type checking and can't do much other
   correctness checking.  If you screw up, it will bite you.

   Glossary of list terms:

     - "front": The first element in a list.  Undefined in an
       empty list.  Returned by pqueue_front().

     - "back": The last element in a list.  Undefined in an empty
       list.  Returned by pqueue_back().

     - "tail": The element figuratively just after the last
       element of a list.  Well defined even in an empty list.
       Returned by pqueue_end().  Used as the end sentinel for an
       iteration from front to back.

     - "beginning": In a non-empty list, the front.  In an empty
       list, the tail.  Returned by pqueue_begin().  Used as the
       starting point for an iteration from front to back.

     - "head": The element figuratively just before the first
       element of a list.  Well defined even in an empty list.
       Returned by pqueue_rend().  Used as the end sentinel for an
       iteration from back to front.

     - "reverse beginning": In a non-empty list, the back.  In an
       empty list, the head.  Returned by pqueue_rbegin().  Used as
       the starting point for an iteration from back to front.

     - "interior element": An element that is not the head or
       tail, that is, a real list element.  An empty list does
       not have any interior elements.
*/

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* List element. */
struct pqueue_elem 
  {
    struct pqueue_elem *prev;     /* Previous list element. */
    struct pqueue_elem *next;     /* Next list element. */
    int priority;
  };

/* List. */
struct pqueue 
  {
    struct pqueue_elem head;      /* List head. */
    struct pqueue_elem tail;      /* List tail. */
  };

/* Converts pointer to list element pqueue_elem into a pointer to
   the structure that pqueue_elem is embedded inside.  Supply the
   name of the outer structure STRUCT and the member name MEMBER
   of the list element.  See the big comment at the top of the
   file for an example. */
#define pqueue_entry(pqueue_elem, STRUCT, MEMBER)           \
        ((STRUCT *) ((uint8_t *) &(pqueue_elem)->next     \
                     - offsetof (STRUCT, MEMBER.next)))

/* List initialization.

   A list may be initialized by calling pqueue_init():

       struct pqueue my_list;
       pqueue_init (&my_list);

   or with an initializer using pqueue_INITIALIZER:

       struct pqueue my_list = pqueue_INITIALIZER (my_list); */
#define pqueue_INITIALIZER(NAME) { { NULL, &(NAME).tail }, \
                                 { &(NAME).head, NULL } }

void pqueue_init (struct pqueue *);

/* List traversal. */
struct pqueue_elem *pqueue_begin (struct pqueue *);
struct pqueue_elem *pqueue_next (struct pqueue_elem *);
struct pqueue_elem *pqueue_end (struct pqueue *);

struct pqueue_elem *pqueue_prev (struct pqueue_elem *);

struct pqueue_elem *pqueue_head (struct pqueue *);
struct pqueue_elem *pqueue_tail (struct pqueue *);

/* List insertion. */
void pqueue_insert (struct pqueue_elem *, struct pqueue_elem *);

/* List removal. */
struct pqueue_elem *pqueue_remove (struct pqueue_elem *);
struct pqueue_elem *pqueue_pop_front (struct pqueue *);

/* List elements. */
struct pqueue_elem *pqueue_front (struct pqueue *);
struct pqueue_elem *pqueue_back (struct pqueue *);

/* List properties. */
size_t pqueue_size (struct pqueue *);
bool pqueue_empty (struct pqueue *);

/* Compares the value of two list elements A and B, given
   auxiliary data AUX.  Returns true if A is less than B, or
   false if A is greater than or equal to B. */
typedef bool pqueue_less_func (const struct pqueue_elem *a,
                             const struct pqueue_elem *b,
                             void *aux);

/* Operations on lists with ordered elements. */
void list_sort (struct list *,
                list_less_func *, void *aux);
void pqueue_insert_ordered (struct pqueue *, struct pqueue_elem *,
                          pqueue_less_func *, void *aux);
void pqueue_unique (struct pqueue *, struct pqueue *duplicates,
                  pqueue_less_func *, void *aux);

/* Max and min. */
struct pqueue_elem *pqueue_max (struct pqueue *, pqueue_less_func *, void *aux);
struct pqueue_elem *pqueue_min (struct pqueue *, pqueue_less_func *, void *aux);

#endif /* lib/kernel/list.h */
