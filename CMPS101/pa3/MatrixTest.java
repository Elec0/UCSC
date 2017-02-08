/*
 * Name: Aaron Steele, atsteele
 * Class: CMPS101
 * Project: Pa3
 */


class MatrixTest
{
	public static void main(String[] args)
	{
		System.out.println("--ChangeEntry--");
		Matrix m = new Matrix(3);
		m.changeEntry(1, 1, 1.0);
		m.changeEntry(1, 2, 2.0);
		m.changeEntry(1, 3, 3.0);
		
		m.changeEntry(2, 1, 4.0);
		m.changeEntry(2, 2, 5.0);
		m.changeEntry(2, 3, 6.0);
		
		m.changeEntry(3, 1, 7.0);
		m.changeEntry(3, 2, 8.0);
		m.changeEntry(3, 3, 9.0);
		
		Matrix n = new Matrix(3);
		n.changeEntry(1, 1, 1);
		n.changeEntry(1, 3, 1);
		n.changeEntry(3, 1, 1);
		n.changeEntry(3, 2, 1);
		n.changeEntry(3, 3, 1);
		
		System.out.println("-M-");
		System.out.println(m.toString());
		System.out.println("NNZ: " + m.getNNZ());
		/*System.out.println("-N-");
		System.out.println(n.toString());
		System.out.println("NNZ: " + n.getNNZ());
		
		System.out.println("--Copy--");
		
		System.out.println(n.toString());
		System.out.println("NNZ: " + n.getNNZ());
		
		System.out.println("--Mult 1.5--");
		m = m.scalarMult(1.5d);
		System.out.println(m.toString());
		
		System.out.println("--Add M+M--");
		Matrix a = m.add(m);
		System.out.println(a.toString());
		
		System.out.println("--Sub M-N--");
		Matrix s = m.sub(n);
		System.out.println(s.toString());
		*/
		System.out.println("--Transpose M--");
		Matrix t = m.transpose();
		System.out.println(t.toString());
		
		/*System.out.println("--Mult M*N--");
		Matrix mu = m.mult(n);
		System.out.println(mu.toString());
		
		System.out.println("--Mult N*N--");
		Matrix muNN = n.mult(n);
		System.out.println(muNN.toString());
		
		System.out.println("--MakeZero--");
		m.makeZero();
		System.out.println(m.toString());
		System.out.println("NNZ: " + m.getNNZ());*/
	}
}