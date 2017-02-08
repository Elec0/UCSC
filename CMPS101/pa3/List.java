/*
 * Name: Aaron Steele, atsteele
 * Class: CMPS101
 * Project: Pa3
 */

public class List 
{
    // Private inner classes
    private class Node
    {
        // Fields
        private Node prev, next;
        private Object data;
        
        // Constructors
        // Blank constructor
        public Node()
        {
            prev = null;
            next = null;
            data = null; // eh
        }
        // Node in the middle of the list
        public Node(Object data, Node prev, Node next)
        {
            this.data = data;
            this.prev = prev;
            this.next = next;
        }
        
        // Access functions
        public Object data()
        {
            return data;
        }
        public Node next()
        {
            return next;
        }
        public Node prev()
        {
            return prev;
        }
        
        // Manipulation procedures
        public void setData(Object data)
        {
            this.data = data;
        }
        public void setNext(Node next)
        {
            this.next = next;
        }
        public void setPrev(Node prev)
        {
            this.prev = prev;
        }
        
        // Other methods
        @Override
        public boolean equals(Object x)
        {
        	// Don't need to bother calling .equals if they aren't even the same class
        	if(x instanceof Node)
        	{
        		// Call the object's equals method, since it's an object
        		return ((Node) x).data().equals(this.data);
        	}
        	return false;
        }
        
        @Override
        public String toString()
        {
            return null;
        }
    }
    

    // Fields
    private int index, length;
    private Node front, back, cursor;
    
    
    // Constructors
    public List()
    {
        index = -1;
        length = 0;
        front = null;
        back = null;
        cursor = null;
    }
    
    // Access functions
    /**
     * Length of the list
     * @return
     */
    public int length()
    {
        return length;
    }
    /**
     * Index of cursor. If not defined, -1.
     * @return
     */
    public int index()
    {
        if(cursor != null)
            return index;
        else
            return -1;
    }
    /**
     * Pre: length > 0
     * @return Node at front of list
     */
    public Object front()
    {
        if(length() <= 0)
            throw new RuntimeException("front(): length <= 0");
        return front.data();
    }
    /**
     * Pre: length > 0
     * @return Node at back of list
     */
    public Object back()
    {
        if(length() <= 0)
            throw new RuntimeException("back(): length <= 0");
        return back.data();
    }
    /**
     * Pre: length > 0
     * @return Node at cursor position
     */
    public Object get()
    {
        if(length() <= 0)
            throw new RuntimeException("get(): length <= 0");
        return cursor.data();
    }
    
    @Override
    public boolean equals(Object x)
    {
        Node cur = front;
        Node LCur = ((List) x).front;
        
        while(cur != null)
        {
            // If L is null before our list is, it's necessarily not equal
            if(LCur == null || !LCur.data().equals(cur.data()))
                return false;
            cur = cur.next();
            LCur = LCur.next();
        }
        return true;
    }
    
    // Manipulation procedures
    /**
     * Reset list to empty
     */
    public void clear()
    {
        front = null;
        back = null;
        cursor = null;
        index = -1;
        length = 0;
    }
    /**
     * If list is not empty, put cursor at front element
     * Else, do nothing
     */
    public void moveFront()
    {
        if(length() > 0)
        {
            cursor = front;
            index = 0;
        }
    }
    /**
     * If list is not empty, put cursor at end element
     * Else, do nothing
     */
    public void moveBack()
    {
        if(length() > 0)
        {
            cursor = back;
            index = length() - 1;
        }
    }
    /**
     * If cursor defined, if not at beginning of list, move cursor back. Else, set cursor to undefined. Else, do nothing
     */
    public void movePrev()
    {
        if(cursor != null)
        {
            if(index() > 0)
            {
                cursor = cursor.prev();
                index--;
            }
            else
            {
                cursor = null;
            }
        }
    }
    /**
     * If cursor defined, if not at end of list, move cursor forward. Else, set cursor to undefined. Else, do nothing
     */
    public void moveNext()
    {
        if(cursor != null)
        {
            if(index() != length() - 1)
            {
                cursor = cursor.next();
                index++;
            }
            else
            {
                cursor = null;
            }
        }
    }
    /**
     * Insert new element.
     * If list is non-empty, put before front element
     * @param data
     */
    public void prepend(Object data)
    {
        Node n = new Node(data, null, front);
        if(length() == 0)
            back = n;
        if(front != null)
            front.prev = n;
        front = n;
        length++;
        
    }
    /**
     * Insert new element.
     * If list is non-empty, put after back element
     * @param data
     */
    public void append(Object data)
    {
        Node n = new Node(data, back, null);
        if(length() == 0)
            front = n;
        if(back != null)
            back.next = n;
        back = n;
        length++;
        
    }
    /**
     * Insert new element before cursor
     * Pre: length>0, index>=0
     * @param data
     */
    public void insertBefore(Object data)
    {
        if(length() <= 0)
            throw new RuntimeException("insertBefore(): length <= 0");
        if(index() < 0)
            throw new RuntimeException("insertBefore(): index < 0");
        
        Node n = new Node(data, cursor.prev(), cursor);
        if(cursor.prev() != null)
            cursor.prev().setNext(n);
        else // If there was nothing before the cursor, cursor was at front, and we need to update front
            front = n;
        cursor.setPrev(n);
        length++;
    }
    /**
     * Insert new element after cursor
     * Pre: length>0, index>=0
     * @param data
     */
    public void insertAfter(Object data)
    {
        if(length() <= 0)
            throw new RuntimeException("insertAfter(): length <= 0");
        if(index() < 0)
            throw new RuntimeException("insertAfter(): index < 0");
        
        Node n = new Node(data, cursor, cursor.next());
        if(cursor.next() != null)
            cursor.next().setPrev(n);
        else // If there was nothing after the cursor, cursor was at back, and we need to update back
            back = n;
        cursor.setNext(n);
        length++;
    }
    /**
     * Delete front element
     * Pre: length>0
     */
    public void deleteFront()
    {
        if(length() <= 0)
            throw new RuntimeException("deleteFront(): length <= 0");
        
        // Just dereference the front node. Garbage collection will take care of the rest
        front = front.next();
        front.setPrev(null);
        if(index() == 0) // If cursor was at front, repoint it to the current front
        {
            cursor = front;
        }
        length--;
        
    }
    /**
     * Delete back element
     * Pre: length>0
     */
    public void deleteBack()
    {
        if(length() <= 0)
            throw new RuntimeException("deleteBack(): length <= 0");
        
        // Dereference back node
        back = back.prev();
        back.setNext(null);
        if(index() == length() - 1) // If cursor was at back, repoint it to back
        {
            cursor = back;
        }
        length--;
        index--; // Also decrease index by 1, as we lost 1 element
        
    }
    /**
     * Delete cursor element, making cursor undefined
     * Pre: length>0, index>=0
     */
    public void delete()
    {
        if(length() <= 0)
            throw new RuntimeException("insertAfter(): length <= 0");
        if(index() < 0)
            throw new RuntimeException("insertAfter(): index < 0");
        
        if(cursor.prev() != null)
        	cursor.prev().setNext(cursor.next());
        if(cursor.next() != null)
        	cursor.next().setPrev(cursor.prev());
        length--;

        if(index() == 0) // Cursor was at front, repoint front to new front
        	front = cursor.next();
        if(index() == length() - 1) // Cursor was at back, repoint back to new back
        	back = cursor.prev();
        
        cursor = null;
        if(index() > 0)
            index--; // Correct index
        
    }
    
    // Other methods
    @Override
    public String toString()
    {
        String ret = "";
        Node cur = front;
        while(cur != null)
        {
            ret += cur.data().toString() + " ";
            cur = cur.next();
        }
        ret.trim();
        
        return ret;
    }
}
