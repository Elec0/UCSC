#include "devices/timer.h"
#include <debug.h>
#include <inttypes.h>
#include <round.h>
#include <stdio.h>
#include <kernel/list.h>
#include "devices/pit.h"
#include "threads/interrupt.h"
#include "threads/synch.h"
#include "threads/thread.h"
   
/* See [8254] for hardware details of the 8254 timer chip. */

#if TIMER_FREQ < 19
#error 8254 timer requires TIMER_FREQ >= 19
#endif
#if TIMER_FREQ > 1000
#error TIMER_FREQ <= 1000 recommended
#endif

/* A linked list element. (From tests/internal/list.c) */
struct value 
  {
    struct list_elem elem;      /* List element. */
    struct thread* value;        /* Item value. */
  };
  
// Number of timer ticks since OS booted.
static int64_t ticks;

// Number of loops per timer tick.   Initialized by timer_calibrate(). 
static unsigned loops_per_tick;

static bool too_many_loops (unsigned loops);
static void busy_wait (int64_t loops);
static intr_handler_func timer_interrupt;
static void real_time_delay (int64_t num, int32_t denom);
static void real_time_sleep (int64_t num, int32_t denom);

static struct list list;



/* 
 * Sets up the timer to interrupt TIMER_FREQ times per second,
 * and registers the corresponding interrupt. 
 */
void 
timer_init (void) 
{
   list_init(&list);
   
   pit_configure_channel (0, 2, TIMER_FREQ);
   intr_register_ext (0x20, timer_interrupt, "8254 Timer");
}

/* 
 * Calibrates loops_per_tick, used to implement brief delays. 
 */
void 
timer_calibrate (void) 
{
   unsigned high_bit, test_bit;

   ASSERT (intr_get_level () == INTR_ON);
   printf ("Calibrating timer...   ");

   /* Approximate loops_per_tick as the largest power-of-two
       still less than one timer tick. */
   loops_per_tick = 1u << 10;
   while (!too_many_loops (loops_per_tick << 1)) 
      {
         loops_per_tick <<= 1;
         ASSERT (loops_per_tick != 0);
      }

   /* Refine the next 8 bits of loops_per_tick. */
   high_bit = loops_per_tick;
   for (test_bit = high_bit >> 1; test_bit != high_bit >> 10; test_bit >>= 1)
      if (!too_many_loops (high_bit | test_bit))
         loops_per_tick |= test_bit;

   printf ("%'"PRIu64" loops/s.\n", (uint64_t) loops_per_tick * TIMER_FREQ);
}

/* 
 * Returns the number of timer ticks since the OS booted. 
 */
int64_t
timer_ticks (void) 
{
   enum intr_level old_level = intr_disable ();
   int64_t t = ticks;
   intr_set_level (old_level);
   return t;
}

/* 
 * Returns the number of timer ticks elapsed since THEN, which
 * should be a value once returned by timer_ticks(). 
 */
int64_t
timer_elapsed (int64_t then) 
{
   return timer_ticks () - then;
}

/* Returns true if the ticks the thread should wake up in A > B
   Taken from the test file list.c
*/
static bool
value_less (const struct list_elem *a_, const struct list_elem *b_,
            void *aux UNUSED)
{
  const struct thread *a = list_entry (a_, struct thread, elem);
  const struct thread *b = list_entry (b_, struct thread, elem);
  
  return a->wakeup < b->wakeup;
}


/* 
 * Sleeps for approximately TICKS timer ticks.
 */
void
timer_sleep (int64_t ticks)
{
   int64_t start = timer_ticks();

   // For alarm-negative
   if(ticks <= 0)
      return;
   
   // 1. Save wakeup time (start + ticks) in current thread
   thread_current()->wakeup = start + ticks;
   
   // Add this thread to a list
   // Order this by wakeup so it's easy to check and things can be popped
   //    if they're finished
   list_insert_ordered(&list, &thread_current()->elem, value_less, NULL);
   
   // Gotten from lecture
   // 2. Call whatever function puts the current thread to sleep
   intr_disable(); // Must have interrupts off to use thread_block
   thread_block(); // Put the thread to sleep
   intr_enable(); // Turn interrupts back on
}

/* 
 * Sleeps for approximately MS milliseconds.   
 * Interrupts must be turned on. 
 */
void
timer_msleep (int64_t ms) 
{
   real_time_sleep (ms, 1000);
}

/* 
 * Sleeps for approximately US microseconds.   
 * Interrupts must be turned on. 
 */
void
timer_usleep (int64_t us) 
{
   real_time_sleep (us, 1000 * 1000);
}

/* 
 * Sleeps for approximately NS nanoseconds.   
 * Interrupts must be turned on. 
 */
void
timer_nsleep (int64_t ns) 
{
   real_time_sleep (ns, 1000 * 1000 * 1000);
}

/* 
 * Busy-waits for approximately MS milliseconds.   
 * Interrupts need not be turned on.
 *
 * Busy waiting wastes CPU cycles, and busy waiting with
 * interrupts off for the interval between timer ticks or longer
 * will cause timer ticks to be lost. Thus, use timer_msleep() 
 * instead if interrupts are enabled. 
 */
void
timer_mdelay (int64_t ms) 
{
   real_time_delay (ms, 1000);
}

/* 
 * Sleeps for approximately US microseconds.   
 * Interrupts need not be turned on.
 *
 * Busy waiting wastes CPU cycles, and busy waiting with
 * interrupts off for the interval between timer ticks or longer
 * will cause timer ticks to be lost. Thus, use timer_usleep()
 * instead if interrupts are enabled. 
 */
void
timer_udelay (int64_t us) 
{
   real_time_delay (us, 1000 * 1000);
}

/* 
 * Sleeps execution for approximately NS nanoseconds.   Interrupts
 * need not be turned on.
 *
 * Busy waiting wastes CPU cycles, and busy waiting with
 * interrupts off for the interval between timer ticks or longer
 * will cause timer ticks to be lost.   Thus, use timer_nsleep()
 *   instead if interrupts are enabled.
 */
void
timer_ndelay (int64_t ns) 
{
   real_time_delay (ns, 1000 * 1000 * 1000);
}

/* 
 * Prints timer statistics. 
 */
void
timer_print_stats (void) 
{
   printf ("Timer: %"PRId64" ticks\n", timer_ticks ());
}

/* 
 * Timer interrupt handler. 
 */
static void
timer_interrupt (struct intr_frame *args UNUSED)
{
   ticks++;

   
   // Check the list for threads whose wakeup timer is finished
   struct list_elem *e;
   struct thread *t;
   
   // Pulled from list.h example comments
   while(!list_empty(&list))
   {
      // Don't pop it because it might not be finished yet
      e = list_front(&list);
      t = list_entry(e, struct thread, elem);
      
      // If it isn't time for the first thread to wake up,
      // then it's not time for any of them to wake up.
      // Also we need to stop the loop here otherwise it's infinite
      if(t->wakeup > ticks)
         break;
      // If we get here then obviously the prior condition is false, no need for another
      // Also remove it from the list
      // NOTE: It is safe to remove the element while iterating over the list
      //    this is because e.tail is still pointing to the same place, just
      //    e.tail.head is no longer e, which is fine for our purposes.
      list_remove(e);
      
      // Apparently the OS throws a hissy fit if you remove the thread from the list
      // BEFORE you unblock it. Who would have guessed.
      thread_unblock(t);

   }
   
   thread_tick();
}

/* 
 * Returns true if LOOPS iterations waits for more than one timer
 * tick, false otherwise. 
 */
static bool
too_many_loops (unsigned loops)
{
   /* Wait for a timer tick. */
   int64_t start = ticks;
   while (ticks == start)
      barrier ();

   /* Run LOOPS loops. */
   start = ticks;
   busy_wait (loops);

   /* If the tick count changed, we iterated too long. */
   barrier ();
   return start != ticks;
}

/* 
 * Iterates through a simple loop LOOPS times, for implementing
 * brief delays.
 *
 * Marked NO_INLINE because code alignment can significantly
 * affect timings, so that if this function was inlined
 * differently in different places the results would be difficult
 * to predict. 
 */
static void NO_INLINE
busy_wait (int64_t loops) 
{
   while (loops-- > 0)
      barrier ();
}

/* 
 * Sleep for approximately NUM/DENOM seconds. 
 */
static void
real_time_sleep (int64_t num, int32_t denom) 
{
   /* Convert NUM/DENOM seconds into timer ticks, rounding down.
               
            (NUM / DENOM) s               
       ---------------------- = NUM * TIMER_FREQ / DENOM ticks. 
       1 s / TIMER_FREQ ticks
   */
   int64_t ticks = num * TIMER_FREQ / denom;

   ASSERT (intr_get_level () == INTR_ON);
   if (ticks > 0)
      {
         /* We're waiting for at least one full timer tick.   Use
             timer_sleep() because it will yield the CPU to other
             processes. */                        
         timer_sleep (ticks); 
      }
   else 
      {
         /* Otherwise, use a busy-wait loop for more accurate
             sub-tick timing. */
         real_time_delay (num, denom); 
      }
}

/* 
 * Busy-wait for approximately NUM/DENOM seconds. 
 */
static void
real_time_delay (int64_t num, int32_t denom)
{
   /* Scale the numerator and denominator down by 1000 to avoid
       the possibility of overflow. */
   ASSERT (denom % 1000 == 0);
   busy_wait (loops_per_tick * num / 1000 * TIMER_FREQ / (denom / 1000)); 
}
