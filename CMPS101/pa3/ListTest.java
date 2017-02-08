/*
 * Name: Aaron Steele, atsteele
 * Class: CMPS101
 * Project: Pa3
 */


class ListTest
{
	public static void main(String[] args)
	{
		List l = new List();
		List nest = new List();
		nest.append("Nested lists.");
		nest.append(-1542);
		
		l.append(12);
		l.append(5.7D);
		l.moveFront();
		l.insertAfter("Testing12");
		l.append(nest);
		l.prepend("First");
		
		System.out.println(l.toString());
		l.moveBack();
		System.out.println(l.get());
		System.out.println(l.equals(nest));
		l.moveFront();
		l.delete();
		System.out.println(l.toString());
		nest.clear();
		System.out.println(l.toString());
		l.clear();
		System.out.println(l.toString());
		
	}
}