
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "List.h"

// ** Structs **

typedef struct NodeObj 
{
    int data;
    struct NodeObj* next;
    struct NodeObj* prev;
} NodeObj;

typedef NodeObj* Node;

typedef struct ListObj
{
    Node front, back, cursor;
    int index, length;
} ListObj;


// ** Constructors-destructors **

// Creates new Node.
Node newNode(int data)
{
    Node n = malloc(sizeof(NodeObj));
    n->data = data;
    n->next = NULL;
    n->prev = NULL;
    return n;
}

// Creates new Node with prev and next parameters
Node newNodePN(int data, Node prev, Node next)
{
    Node n = malloc(sizeof(NodeObj));
    n->data = data;
    n->next = next;
    n->prev = prev;
    return n;
}

// Frees memory of pN, and sets *pN to NULL.
void freeNode(Node* pN)
{
    if (pN != NULL && *pN != NULL)
    {
        free(*pN);
        *pN = NULL;
    }
}

// Recursively frees all nodes starting at pN.
void freeAllNodes(Node* pN)
{
    if (pN != NULL && *pN != NULL)
    {
        if ((*pN)->next != NULL)
            freeAllNodes(&((*pN)->next));
        free(*pN);
        *pN = NULL;
    }
}

// List constructor
List newList(void)
{
    List L = malloc(sizeof(ListObj));
    L->front = NULL;
    L->back = NULL;
    L->cursor = NULL;
    L->length = 0;
    L->index = -1;
    return L;
}

// Removes all memory associated with the List.
// Also needs to delete all Nodes within the list, I think.
void freeList(List* pL)
{
    if (pL != NULL && *pL != NULL)
    {
        // Remove all node memory from list.
        freeAllNodes(&(*pL)->front);

        free(*pL);
        *pL = NULL;
    }
}

// ** Access functions **

// Return length of the list
int length(List L)
{
    if (L == NULL) {
        printf("List Error: length(): L is NULL.\n");
        exit(1);
    }
    return L->length;
}

// Return index of cursor. If not defined, return -1.
int index(List L)
{
    if (L == NULL) {
        printf("List Error: index(): L is NULL.\n");
        exit(1);
    }
    if (L->cursor == NULL)
        return -1;
    else
        return L->index;
}

// Pre: length > 0
// Return data at front of list
int front(List L)
{
    if (L == NULL) {
        printf("List Error: front(): L is NULL.\n");
        exit(1);
    }
    if (length(L) <= 0)
    {
        printf("List Error: front(): length <= 0.\n");
        exit(1);
    }
    return L->front->data;
}

// Pre: length > 0
// Return data at back of list.
int back(List L)
{
    if (L == NULL) {
        printf("List Error: back(): L is NULL.\n");
        exit(1);
    }
    if (length(L) <= 0)
    {
        printf("List Error: back(): length <= 0.\n");
        exit(1);
    }
    return L->back->data;
}

// Pre: length > 0
// Return data at cursor position
int get(List L)
{
    if (L == NULL) {
        printf("List Error: get(): L is NULL.\n");
        exit(1);
    }
    if (length(L) <= 0)
    {
        printf("List Error: get(): length <= 0.\n");
        exit(1);
    }
    return L->cursor->data;
}

// Returns 1 if lists are equal, 0 if they are not.
// Checks if all elements in the lists are the same in the same positions
int equals(List A, List B)
{
    if (A == NULL || B == NULL) {
        printf("List Error: equals(): A or B is NULL.\n");
        exit(1);
    }

    Node cur = A->front;
    Node LCur = B->front;

    while (cur != NULL)
    {
        // if B is null before A, then it's necessarily not equal
        if (LCur == NULL || LCur->data != cur->data)
            return 0;
        cur = cur->next;
        LCur = LCur->next;
    }
    return 1;
}

// ** Manipulation procedures **

// Reset list to empty
void clear(List L)
{
    if (L == NULL) {
        printf("List Error: clear(): L is NULL.\n");
        exit(1);
    }
    freeNode(&(L->cursor));
    // Free all nodes from start to end.
    freeAllNodes(&(L->front));
    L->index = -1;
    L->length = 0;
}

// If list not empty, put cursor at front.
// Else, do nothing
void moveFront(List L)
{
    if (L == NULL) {
        printf("List Error: moveFront(): L is NULL.\n");
        exit(1);
    }
    if (length(L) > 0)
    {
        L->cursor = L->front;
        L->index = 0;
    }
}

// If list not empty, put cursor at back
// Else, do nothing
void moveBack(List L)
{
    if (L == NULL) {
        printf("List Error: moveBack(): L is NULL.\n");
        exit(1);
    }
    if (length(L) > 0)
    {
        L->cursor = L->back;
        L->index = length(L) - 1;
    }
}

// If cursor defined, if not at beginning of list, move cursor back. Else, set cursor to undefined. Else, do nothing
void movePrev(List L)
{
    if (L == NULL) {
        printf("List Error: movePrev(): L is NULL.\n");
        exit(1);
    }
    if (L->cursor != NULL)
    {
        if (index(L) > 0)
        {
            L->cursor = L->cursor->prev;
            L->index--;
        }
        else
        {
            L->cursor = NULL;
        }
    }
}

// If cursor defined, if not at end of list, move cursor forward. Else, set cursor to undefined. Else, do nothing
void moveNext(List L)
{
    if (L == NULL) {
        printf("List Error: moveNext(): L is NULL.\n");
        exit(1);
    }
    if (L->cursor != NULL)
    {
        if (index(L) != length(L) - 1)
        {
            L->cursor = L->cursor->next;
            L->index++;
        }
        else
        {
            L->cursor = NULL;
        }
    }
}

// Insert new element.
//If list is non-empty, put before front element
void prepend(List L, int data)
{
    if (L == NULL) {
        printf("List Error: prepend(): L is NULL.\n");
        exit(1);
    }
    Node n = newNodePN(data, NULL, L->front);
    if (length(L) == 0)
        L->back = n;
    if (L->front != NULL)
        L->front->prev = n;
    L->front = n;
    L->length++;
}

// Insert new element.
// If list is non-empty, put after back element
void append(List L, int data)
{
    if (L == NULL) {
        printf("List Error: append(): L is NULL.\n");
        exit(1);
    }
    Node n = newNodePN(data, L->back, NULL);
    if (length(L) == 0)
        L->front = n;
    if (L->back != NULL)
        L->back->next = n;
    L->back = n;
    L->length++;
    //printf("Appended to L w/ %d\n", data);
}

// Insert new element before cursor
// Pre: length>0, index>=0
void insertBefore(List L, int data)
{
    if (L == NULL) {
        printf("List Error: insertBefore(): L is NULL.\n");
        exit(1);
    }
    if (length(L) <= 0) {
        printf("List Error: insertBefore(): length <= 0\n");
        exit(1);
    }
    if (index(L) < 0) {
        printf("List Error: insertBefore(): index < 0\n");
        exit(1);
    }

    Node n = newNodePN(data, L->cursor->prev, L->cursor);
    if (L->cursor->prev != NULL)
        L->cursor->prev->next = n;
    else // There was nothing before the cursor, cursor was at front, and we need to update front
        L->front = n;
    L->cursor->prev = n;
    L->length++;
}

// Insert new element after cursor
// Pre: length>0, index>=0
void insertAfter(List L, int data)
{
    if (L == NULL) {
        printf("List Error: insertAfter(): L is NULL.\n");
        exit(1);
    }
    if (length(L) <= 0) {
        printf("List Error: insertAfter(): length <= 0\n");
        exit(1);
    }
    if (index(L) < 0) {
        printf("List Error: insertAfter(): index < 0\n");
        exit(1);
    }

    Node n = newNodePN(data, L->cursor, L->cursor->next);
    if (L->cursor->next != NULL)
        L->cursor->next->prev = n;
    else // If there was nothing after the cursor, cursor was at back, and we need to update back
        L->back = n;
    L->cursor->next = n;
    L->length++;
}

// Delete front element
// Pre: length>0
void deleteFront(List L)
{
    if (L == NULL) {
        printf("List Error: deleteFront(): L is NULL.\n");
        exit(1);
    }
    if (length(L) <= 0) {
        printf("List Error: deleteFront(): length <= 0\n");
        exit(1);
    }
    // We can't do the same as in java and dereference things, unfortunately
    L->front = L->front->next;
    freeNode(&(L->front->prev));
    L->front->prev = NULL;
    if (index(L) == 0) // If cursor was at front, repoint it to the current front
    {
        L->cursor = L->front;
    }
    L->length--;
}

// Delete back element
// Pre: length>0
void deleteBack(List L)
{
    if (L == NULL) {
        printf("List Error: deleteBack(): L is NULL.\n");
        exit(1);
    }
    if (length(L) <= 0) {
        printf("List Error: deleteBack(): length <= 0\n");
        exit(1);
    }
    // Clear back node
    L->back = L->back->prev;
    freeNode(&(L->back->next));
    if (index(L) == length(L) - 1) // If cursor was at back, repoint it to new back
    {
        L->cursor = L->back;
    }
    L->length--;
    L->index--; // Decrease index by 1 because we lost an element
}

// Delete cursor element, making cursor undefined
// Pre: length>0, index>=0
void delete(List L)
{
    if (L == NULL) {
        printf("List Error: delete(): L is NULL.\n");
        exit(1);
    }
    if (length(L) <= 0) {
        printf("List Error: delete(): length <= 0\n");
        exit(1);
    }
    if (index(L) < 0) {
        printf("List Error: delete(): index < 0\n");
        exit(1);
    }

    L->cursor->prev->next = L->cursor->next;
    L->cursor->next->prev = L->cursor->prev;
    L->length--;
    L->cursor = NULL;
    if (index(L) > 0)
        L->index = -1; // Reset index to -1 since cursor is undefined
}

// ** Other functions **

void printList(FILE* out, List L)
{
    if (L == NULL) {
        printf("List Error: printList(): L is NULL.\n");
        exit(1);
    }
    if (out == NULL) {
        printf("List Error: printlist(): out is NULL.\n");
        exit(1);
    }

    Node cur = L->front;
    while (cur != NULL)
    {
        fprintf(out, "%d ", cur->data);
        cur = cur->next;
    }
}

List copyList(List L)
{
    List nL = newList();
    Node cur = L->front;

    while (cur != NULL)
    {
        append(nL, cur->data);
        cur = cur->next;
    }
    return nL;
}