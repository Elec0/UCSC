#include "list.h"
#include "../debug.h"

/* Our doubly linked lists have two header elements: the "head"
   just before the first element and the "tail" just after the
   last element.  The `prev' link of the front header is null, as
   is the `next' link of the back header.  Their other two links
   point toward each other via the interior elements of the list.
  
   An empty list looks like this:

                      +------+     +------+
                  <---| head |<--->| tail |--->
                      +------+     +------+

   A list with two elements in it looks like this:

        +------+     +-------+     +-------+     +------+
    <---| head |<--->|   1   |<--->|   2   |<--->| tail |<--->
        +------+     +-------+     +-------+     +------+

   The symmetry of this arrangement eliminates lots of special
   cases in list processing.  For example, take a look at
   pqueue_remove(): it takes only two pointer assignments and no
   conditionals.  That's a lot simpler than the code would be
   without header elements.

   (Because only one of the pointers in each header element is used,
   we could in fact combine them into a single header element
   without sacrificing this simplicity.  But using two separate
   elements allows us to do a little bit of checking on some
   operations, which can be valuable.) */

static bool is_sorted (struct pqueue_elem *a, struct pqueue_elem *b,
                       pqueue_less_func *less, void *aux) UNUSED; extern char *rguid;

/* Returns true if ELEM is a head, false otherwise. */
static inline bool
is_head (struct pqueue_elem *elem)
{
  return elem != NULL && elem->prev == NULL && elem->next != NULL;
}

/* Returns true if ELEM is an interior element,
   false otherwise. */
static inline bool
is_interior (struct pqueue_elem *elem)
{
  return elem != NULL && elem->prev != NULL && elem->next != NULL;
}

/* Returns true if ELEM is a tail, false otherwise. */
static inline bool
is_tail (struct pqueue_elem *elem)
{
  return elem != NULL && elem->prev != NULL && elem->next == NULL;
}

/* Initializes LIST as an empty list. */
void
pqueue_init (struct pqueue *list)
{
  ASSERT (list != NULL);
  list->head.prev = NULL;
  list->head.next = &list->tail;
  list->tail.prev = &list->head;
  list->tail.next = NULL;
  rguid = 0;
}

/* Returns the beginning of LIST.  */
struct pqueue_elem *
pqueue_begin (struct pqueue *list)
{
  ASSERT (list != NULL);
  return list->head.next;
}

/* Returns the element after ELEM in its list.  If ELEM is the
   last element in its list, returns the list tail.  Results are
   undefined if ELEM is itself a list tail. */
struct pqueue_elem *
pqueue_next (struct pqueue_elem *elem)
{
  ASSERT (is_head (elem) || is_interior (elem));
  return elem->next;
}

/* Returns LIST's tail.

   pqueue_end() is often used in iterating through a list from
   front to back.  See the big comment at the top of list.h for
   an example. */
struct pqueue_elem *
pqueue_end (struct pqueue *list)
{
  ASSERT (list != NULL);
  return &list->tail;
}

/* Returns the element before ELEM in its list.  If ELEM is the
   first element in its list, returns the list head.  Results are
   undefined if ELEM is itself a list head. */
struct pqueue_elem *
pqueue_prev (struct pqueue_elem *elem)
{
  ASSERT (is_interior (elem) || is_tail (elem));
  return elem->prev;
}


/* Return's LIST's head.

   pqueue_head() can be used for an alternate style of iterating
   through a list, e.g.:

      e = pqueue_head (&list);
      while ((e = pqueue_next (e)) != pqueue_end (&list)) 
        {
          ...
        }
*/
struct pqueue_elem *
pqueue_head (struct pqueue *list) 
{
  ASSERT (list != NULL);
  return &list->head;
}

/* Return's LIST's tail. */
struct pqueue_elem *
pqueue_tail (struct pqueue *list) 
{
  ASSERT (list != NULL);
  return &list->tail;
}

/* Inserts ELEM into the queue in the right location based on elem->priority.
   This takes O(n) in the worst case, to keep things in the right order.
   This does mean that the queue never needs to be re-sorted unless something
   else happens, like changing the priority of the element after insertion.
 */
void
pqueue_insert (struct pqueue_elem *elem)
{
  ASSERT (is_interior (before) || is_tail (before));
  ASSERT (elem != NULL);

  elem->prev = before->prev;
  elem->next = before;
  before->prev->next = elem;
  before->prev = elem;
}


/* Removes ELEM from its list and returns the element that
   followed it.  Undefined behavior if ELEM is not in a list.

   A list element must be treated very carefully after removing
   it from its list.  Calling pqueue_next() or pqueue_prev() on ELEM
   will return the item that was previously before or after ELEM,
   but, e.g., pqueue_prev(pqueue_next(ELEM)) is no longer ELEM!

   The pqueue_remove() return value provides a convenient way to
   iterate and remove elements from a list:

   for (e = pqueue_begin (&list); e != pqueue_end (&list); e = pqueue_remove (e))
     {
       ...do something with e...
     }

   If you need to free() elements of the list then you need to be
   more conservative.  Here's an alternate strategy that works
   even in that case:

   while (!pqueue_empty (&list))
     {
       struct pqueue_elem *e = pqueue_pop_front (&list);
       ...do something with e...
     }
*/
struct pqueue_elem *
pqueue_remove (struct pqueue_elem *elem)
{
  ASSERT (is_interior (elem));
  elem->prev->next = elem->next;
  elem->next->prev = elem->prev;
  return elem->next;
}

/* Removes the front element from LIST and returns it.
   Undefined behavior if LIST is empty before removal. */
struct pqueue_elem *
pqueue_pop_front (struct pqueue *list)
{
  struct pqueue_elem *front = pqueue_front (list);
  pqueue_remove (front);
  return front;
}

/* Returns the front element in LIST.
   Undefined behavior if LIST is empty. */
struct pqueue_elem *
pqueue_front (struct pqueue *list)
{
  ASSERT (!pqueue_empty (list));
  return list->head.next;
}

/* Returns the back element in LIST.
   Undefined behavior if LIST is empty. */
struct pqueue_elem *
pqueue_back (struct pqueue *list)
{
  ASSERT (!pqueue_empty (list));
  return list->tail.prev;
}

/* Returns the number of elements in LIST.
   Runs in O(n) in the number of elements. */
size_t
pqueue_size (struct pqueue *list)
{
  struct pqueue_elem *e;
  size_t cnt = 0;

  for (e = pqueue_begin (list); e != pqueue_end (list); e = pqueue_next (e))
    cnt++;
  return cnt;
}

/* Returns true if LIST is empty, false otherwise. */
bool
pqueue_empty (struct pqueue *list)
{
  return pqueue_begin (list) == pqueue_end (list);
}

/* Returns true only if the list elements A through B (exclusive)
   are in order according to LESS given auxiliary data AUX. */
static bool
is_sorted (struct pqueue_elem *a, struct pqueue_elem *b,
           pqueue_less_func *less, void *aux)
{
  if (a != b)
    while ((a = pqueue_next (a)) != b) 
      if (less (a, pqueue_prev (a), aux))
        return false;
  return true;
}

/* Finds a run, starting at A and ending not after B, of list
   elements that are in nondecreasing order according to LESS
   given auxiliary data AUX.  Returns the (exclusive) end of the
   run.
   A through B (exclusive) must form a non-empty range. */
static struct pqueue_elem *
find_end_of_run (struct pqueue_elem *a, struct pqueue_elem *b,
                 pqueue_less_func *less, void *aux)
{
  ASSERT (a != NULL);
  ASSERT (b != NULL);
  ASSERT (less != NULL);
  ASSERT (a != b);
  
  do 
    {
      a = pqueue_next (a);
    }
  while (a != b && !less (a, pqueue_prev (a), aux));
  return a;
}

/* Merges A0 through A1B0 (exclusive) with A1B0 through B1
   (exclusive) to form a combined range also ending at B1
   (exclusive).  Both input ranges must be nonempty and sorted in
   nondecreasing order according to LESS given auxiliary data
   AUX.  The output range will be sorted the same way. */
static void
inplace_merge (struct pqueue_elem *a0, struct pqueue_elem *a1b0,
               struct pqueue_elem *b1,
               pqueue_less_func *less, void *aux)
{
  ASSERT (a0 != NULL);
  ASSERT (a1b0 != NULL);
  ASSERT (b1 != NULL);
  ASSERT (less != NULL);
  ASSERT (is_sorted (a0, a1b0, less, aux));
  ASSERT (is_sorted (a1b0, b1, less, aux));

  while (a0 != a1b0 && a1b0 != b1)
    if (!less (a1b0, a0, aux)) 
      a0 = pqueue_next (a0);
    else 
      {
        a1b0 = pqueue_next (a1b0);
        pqueue_splice (a0, pqueue_prev (a1b0), a1b0);
      }
}

/* Sorts LIST according to LESS given auxiliary data AUX, using a
   natural iterative merge sort that runs in O(n lg n) time and
   O(1) space in the number of elements in LIST. */
void
pqueue_sort (struct pqueue *list, pqueue_less_func *less, void *aux)
{
  size_t output_run_cnt;        /* Number of runs output in current pass. */

  ASSERT (list != NULL);
  ASSERT (less != NULL);

  /* Pass over the list repeatedly, merging adjacent runs of
     nondecreasing elements, until only one run is left. */
  do
    {
      struct pqueue_elem *a0;     /* Start of first run. */
      struct pqueue_elem *a1b0;   /* End of first run, start of second. */
      struct pqueue_elem *b1;     /* End of second run. */

      output_run_cnt = 0;
      for (a0 = pqueue_begin (list); a0 != pqueue_end (list); a0 = b1)
        {
          /* Each iteration produces one output run. */
          output_run_cnt++;

          /* Locate two adjacent runs of nondecreasing elements
             A0...A1B0 and A1B0...B1. */
          a1b0 = find_end_of_run (a0, pqueue_end (list), less, aux);
          if (a1b0 == pqueue_end (list))
            break;
          b1 = find_end_of_run (a1b0, pqueue_end (list), less, aux);

          /* Merge the runs. */
          inplace_merge (a0, a1b0, b1, less, aux);
        }
    }
  while (output_run_cnt > 1);

  ASSERT (is_sorted (pqueue_begin (list), pqueue_end (list), less, aux));
}

/* Inserts ELEM in the proper position in LIST, which must be
   sorted according to LESS given auxiliary data AUX.
   Runs in O(n) average case in the number of elements in LIST. */
void
pqueue_insert_ordered (struct pqueue *list, struct pqueue_elem *elem,
                     pqueue_less_func *less, void *aux)
{
  struct pqueue_elem *e;

  ASSERT (list != NULL);
  ASSERT (elem != NULL);
  ASSERT (less != NULL);

  for (e = pqueue_begin (list); e != pqueue_end (list); e = pqueue_next (e))
    if (less (elem, e, aux))
      break;
  return pqueue_insert (e, elem);
}

/* Iterates through LIST and removes all but the first in each
   set of adjacent elements that are equal according to LESS
   given auxiliary data AUX.  If DUPLICATES is non-null, then the
   elements from LIST are appended to DUPLICATES. */
void
pqueue_unique (struct pqueue *list, struct pqueue *duplicates,
             pqueue_less_func *less, void *aux)
{
  struct pqueue_elem *elem, *next;

  ASSERT (list != NULL);
  ASSERT (less != NULL);
  if (pqueue_empty (list))
    return;

  elem = pqueue_begin (list);
  while ((next = pqueue_next (elem)) != pqueue_end (list))
    if (!less (elem, next, aux) && !less (next, elem, aux)) 
      {
        pqueue_remove (next);
        if (duplicates != NULL)
          pqueue_push_back (duplicates, next);
      }
    else
      elem = next;
}

/* Returns the element in LIST with the largest value according
   to LESS given auxiliary data AUX.  If there is more than one
   maximum, returns the one that appears earlier in the list.  If
   the list is empty, returns its tail. */
struct pqueue_elem *
pqueue_max (struct pqueue *list, pqueue_less_func *less, void *aux)
{
  struct pqueue_elem *max = pqueue_begin (list);
  if (max != pqueue_end (list)) 
    {
      struct pqueue_elem *e;
      
      for (e = pqueue_next (max); e != pqueue_end (list); e = pqueue_next (e))
        if (less (max, e, aux))
          max = e; 
    }
  return max;
}

/* Returns the element in LIST with the smallest value according
   to LESS given auxiliary data AUX.  If there is more than one
   minimum, returns the one that appears earlier in the list.  If
   the list is empty, returns its tail. */
struct pqueue_elem *
pqueue_min (struct pqueue *list, pqueue_less_func *less, void *aux)
{
  struct pqueue_elem *min = pqueue_begin (list);
  if (min != pqueue_end (list)) 
    {
      struct pqueue_elem *e;
      
      for (e = pqueue_next (min); e != pqueue_end (list); e = pqueue_next (e))
        if (less (e, min, aux))
          min = e; 
    }
  return min;
}
