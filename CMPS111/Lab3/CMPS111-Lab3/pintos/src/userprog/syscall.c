/* 
 * This file is derived from source code for the Pintos
 * instructional operating system which is itself derived
 * from the Nachos instructional operating system. The 
 * Nachos copyright notice is reproduced in full below. 
 *
 * Copyright (C) 1992-1996 The Regents of the University of California.
 * All rights reserved.
 *
 * Permission to use, copy, modify, and distribute this software
 * and its documentation for any purpose, without fee, and
 * without written agreement is hereby granted, provided that the
 * above copyright notice and the following two paragraphs appear
 * in all copies of this software.
 *
 * IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO
 * ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR
 * CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF THIS SOFTWARE
 * AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY OF CALIFORNIA
 * HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE.  THE SOFTWARE PROVIDED HEREUNDER IS ON AN "AS IS"
 * BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATION TO
 * PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
 * MODIFICATIONS.
 *
 * Modifications Copyright (C) 2017-2018 David C. Harrison. 
 * All rights reserved.
 */

#include <stdio.h>
#include <syscall-nr.h>
#include <list.h>

#include "devices/shutdown.h"
#include "devices/input.h"
#include "filesys/filesys.h"
#include "filesys/file.h"
#include "filesys/inode.h"
#include "filesys/directory.h"
#include "threads/palloc.h"
#include "threads/malloc.h"
#include "threads/interrupt.h"
#include "threads/thread.h"
#include "threads/vaddr.h"
#include "userprog/syscall.h"
#include "userprog/process.h"
#include "userprog/umem.h"

static void syscall_handler(struct intr_frame *);

static void write_handler(struct intr_frame *);
static void exit_handler(struct intr_frame *);
static void create_handler(struct intr_frame *);
static void open_handler(struct intr_frame *);
static void read_handler(struct intr_frame *);
static void filesize_handler(struct intr_frame *);
static void close_handler(struct intr_frame *);
static struct file * get_file(int fd);

void
syscall_init (void)
{
  intr_register_int (0x30, 3, INTR_ON, syscall_handler, "syscall");
  
  g_file_num = 3;
}

static void
syscall_handler(struct intr_frame *f)
{
  int syscall;
  ASSERT( sizeof(syscall) == 4 ); // assuming x86

  // The system call number is in the 32-bit word at the caller's stack pointer.
  umem_read(f->esp, &syscall, sizeof(syscall));

  // Store the stack pointer esp, which is needed in the page fault handler.
  // Do NOT remove this line
  thread_current()->current_esp = f->esp;

  switch (syscall) {
  case SYS_HALT: 
    shutdown_power_off();
    break;

  case SYS_EXIT: 
    exit_handler(f);
    break;
  
  // ***** Mine *****
  case SYS_CREATE:
    create_handler(f);
    break;
    
  case SYS_OPEN:
    open_handler(f);
    break;
  
  case SYS_READ:
    read_handler(f);
    break;
    
  case SYS_FILESIZE:
    filesize_handler(f);
    break;
    
  case SYS_CLOSE:
    close_handler(f);
    break;
  // ***** End Mine *****
  
  case SYS_WRITE: 
    write_handler(f);
    break;

  default:
    printf("[ERROR] system call %d is unimplemented!\n", syscall);
    thread_exit();
    break;
  }
}

/****************** System Call Implementations ********************/

void sys_exit(int status) 
{
  printf("%s: exit(%d)\n", thread_current()->name, status);
  thread_exit();
}

static void exit_handler(struct intr_frame *f) 
{
  int exitcode;
  umem_read(f->esp + 4, &exitcode, sizeof(exitcode));

  sys_exit(exitcode);
}

/*
 * BUFFER+0 and BUFFER+size should be valid user addresses
 */
static uint32_t sys_write(int fd, const void *buffer, unsigned size)
{
    ASSERT(fd >= 1);

    umem_check((const uint8_t*) buffer);
    umem_check((const uint8_t*) buffer + size - 1);

    int ret = -1;

    if (fd == 1) { // write to stdout
        putbuf(buffer, size);
        ret = size;
    }
    else
    {
        struct file *f = get_file(fd);
        
        if(!f)
            return -1;
        
        ret = file_write(f, buffer, size);
    }

    return (uint32_t) ret;
}

static void write_handler(struct intr_frame *f)
{
    int fd;
    const void *buffer;
    unsigned size;

    umem_read(f->esp + 4, &fd, sizeof(fd));
    umem_read(f->esp + 8, &buffer, sizeof(buffer));
    umem_read(f->esp + 12, &size, sizeof(size));

    f->eax = sys_write(fd, buffer, size);
}

/****************** Create Syscall ******************/

static bool sys_create (const char *file, off_t size)
{
    // If the file is blank
    if(!file)
    {    
        sys_exit(-1);
        return -1;
    }
    
    bool result;
    result = filesys_create(file, size, false);
    
    return result;
}

static void create_handler(struct intr_frame *f)
{
    const char *file;
    off_t size;
    
    
    umem_read(f->esp + 4, &file, sizeof(file));
    umem_read(f->esp + 8, &size, sizeof(size));
    
    f->eax = sys_create(file, size);
    
}


/****************** Open Syscall ******************/
static int sys_open(const char *file_name)
{
    ASSERT(g_file_num <= 255);
    
    struct file *sys_file;
    
    if(!file_name)
    {
        return -1;
    }
    sys_file = filesys_open(file_name);
    
    if(!sys_file)
    {
        return -1;
    }
    
    // Increment the g_file_num and assign the file to this process.
    sys_file->file_num = g_file_num++;
    
    struct thread *thr = thread_current();
    thr->files[sys_file->file_num] = sys_file;
    
    // Return the external id
    return sys_file->file_num;
}

static void open_handler(struct intr_frame *f)
{
    const char *file;
    
    umem_read(f->esp + 4, &file, sizeof(file));
    
    f->eax = sys_open(file);
}

/****************** Read Syscall ******************/
static int sys_read(int fd, void *buffer, unsigned length)
{
    struct file *f = get_file(fd);
    
    int read; // How much was actually read
    read = file_read(f, buffer, length);
    
    return read;
}

static void read_handler(struct intr_frame *f)
{
    int fd;
    const void *buffer;
    unsigned length;
    
    umem_read(f->esp + 4, &fd, sizeof(fd));
    umem_read(f->esp + 8, &buffer, sizeof(buffer));
    umem_read(f->esp + 12, &length, sizeof(length));
    
    f->eax = sys_read(fd, buffer, length);
}

/****************** Filesize Syscall ******************/
static int sys_filesize(int fd)
{
    ASSERT(fd >= 3);
    
    struct file *f = get_file(fd);
    
    // File is null
    if(!f)
    {
        return -1;
    }
    
    off_t size;
    size = file_length(f);
    
    return (int) size;
}

static void filesize_handler(struct intr_frame *f)
{
    int fd;
    
    umem_read(f->esp + 4, &fd, sizeof(fd));
    
    f->eax = sys_filesize(fd);
}

/****************** Filesize Syscall ******************/
static void sys_close(int fd)
{
    ASSERT(fd >= 3);
    
    struct file *f = get_file(fd);
    
    // If the file doesn't exist anyway, just stop
    if(!f)
    {
        return;
    }
    
    // Actually close the file
    file_close(f);
    
    // Now clear out the entry in the array
    struct thread *t = thread_current();
    t->files[fd] = 0;
    
}

static void close_handler(struct intr_frame *f)
{
    int fd;
    
    umem_read(f->esp + 4, &fd, sizeof(fd));
    
    //f->eax = sys_close(fd);
    sys_close(fd); // close doesn't return anything, do don't put anything in eax?
}

/**
    Simple function to turn a file ID int into the file pointer itself.
**/
static struct file* get_file(int fd)
{
    struct thread *t = thread_current();
    
    if(t->files[fd] == 0)
    {
        return NULL;
    }
    
    struct file *f = t->files[fd];
    return f;
}


