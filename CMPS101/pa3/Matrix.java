/*
 * Name: Aaron Steele, atsteele
 * Class: CMPS101
 * Project: Pa3
 */

class Matrix
{
	
	private class Entry
	{
		private int colData;
		private double val;
		
		public Entry()
		{
			colData = 0;
			val = 0;
		}
		public Entry(int colData, double val)
		{
			this.colData = colData;
			this.val = val;
		}
		
		@Override
		public boolean equals(Object x)
		{
			if(x instanceof Entry)
			{
				if(colData == ((Entry)x).getColData() && val == ((Entry)x).getVal())
					return true;
			}
			return false;
		}
		
		@Override
		public String toString()
		{
			return "(" + colData + ", " + val + ")";
		}
		
		// Access methods
		public int getColData() {
			return colData;
		}

		public void setColData(int colData) {
			this.colData = colData;
		}

		public double getVal() {
			return val;
		}

		public void setVal(double val) {
			this.val = val;
		}
		
		
	}
	
	private List[] matrix;
	private int size;
	
	
	/**
	 * Make a new n x n zero Matrix.
	 * Pre: n >= 1
	 * @param n
	 */
	public Matrix(int n)
	{
		matrix = new List[n];
		size = n;
		
		for(int i = 0; i < matrix.length; ++i)
		{
			matrix[i] = new List();
		}
	}
	
	// Access functions
	/**
	 * Returns n, the number of rows and columns of this matrix
	 * @return
	 */
	public int getSize()
	{
		return size;
	}
	
	/**
	 * Returns number of non-zero entries in this matrix
	 * @return
	 */
	public int getNNZ()
	{
		int result = 0;
		
		for(int i = 0; i < matrix.length; ++i)
		{
			result += matrix[i].length();
		}
		return result;
	}
	
	/**
	 * Overrides Object's equals method
	 */
	@Override
	public boolean equals(Object x)
	{
		if(x instanceof Matrix)
		{
			for(int i = 0; i < matrix.length; ++i)
			{
				if(!matrix[i].equals(((Matrix)x).matrix[i]))
				{
					return false;
				}
			}
			return true;
		}
		return false;
	}
	
	
	// Manipulation procedures
	/**
	 * Sets this matrix to the zero state
	 */
	public void makeZero()
	{
		for(int i = 0; i < matrix.length; ++i)
		{
			matrix[i].clear();
		}
	}
	
	/**
	 * Returns a new matrix having the same entries as this matrix
	 * @return
	 */
	public Matrix copy()
	{
		Matrix m = new Matrix(getSize());
		
		for(int i = 0; i < matrix.length; ++i)
		{
			List row = matrix[i];
			row.moveFront();
			while(row.index() != -1)
			{
				Entry e = (Entry) row.get();
				m.changeEntry(i+1, e.getColData(), e.getVal());
				row.moveNext();
			}
		}
		
		return m;
	}
	
	/**
	 * Retrieves Entry object at row i, col j of the matrix
	 * Pre: 1 <= i <= getSize(), 1 <= j <= getSize()
	 * @param i
	 * @param j
	 * @return Entry object
	 */
	private Entry retrieveEntry(int i, int j)
	{
		if(i < 1 || i > getSize())
			throw new RuntimeException("retrieveEntry(): i out of range.");
		if(j < 1 || j > getSize())
			throw new RuntimeException("retrieveEntry(): j out of range.");
		
		Entry result = null;
		i--;
		List row = matrix[i];
		if(row.length() == 0)
			return result;
		
		row.moveFront();
		for(int k = 0; k < matrix.length; ++k)
		{
			if(row.index() != -1)
			{
				if(((Entry)row.get()).getColData() == j)
				{
					return (Entry)row.get();
				}
			}
			row.moveNext();
		}
		
		return result;
	}
	
	
	/**
	 * Changes ith row, jth column, of this matrix to x.
	 * Pre: 1 <= i <= getSize(), 1 <= j <= getSize()
	 * @param i
	 * @param j
	 * @param x
	 */
	public void changeEntry(int i, int j, double x)
	{
		if(i < 1 || i > getSize())
			throw new RuntimeException("changeEntry(): i out of range.");
		if(j < 1 || j > getSize())
			throw new RuntimeException("changeEntry(): j out of range.");
		
		// Correct indexes. We start at 0 in Java, but in matrices we start at 1.
		i--;
		
		List row = matrix[i];
		// If the jth col already exists, we need to modify it.
		// If it does not, we need to add it in the correct position.
		
		
		// There are no elements in the list, so add the entry
		if(row.length() == 0)
		{
			if(x != 0)
				row.append(new Entry(j, x));
			return;
		}
		
		row.moveFront();
		
		// The most times we need to moveNext is j, because we're looking for
		// 	the jth col
		for(int k = 0; k < j; ++k)
		{
			// If we've run out of objects and haven't found what we're looking for, put the
			//	new entry at the end of the list
			if(row.index() == -1)
			{
				if(x != 0)
					row.append(new Entry(j, x));
				return;
			}
			if(((Entry)row.get()).getColData() == j)
			{
				// The entry already exists, edit it
				if(x != 0)
					((Entry)row.get()).setVal(x);
				else
					row.delete(); // If the value being changed is 0, delete the element.
				return;
			}
			// If we've passed the column without finding it, then it doesn't exist
			// 	and needs to be added
			if(((Entry)row.get()).getColData() > j)
			{
				if(x != 0)
					row.insertBefore(new Entry(j, x));
				return;
			}
			row.moveNext();
		}		
	}
	
	/**
	 * Returns a new matrix that is the scalar product of this matrix with x
	 * @param x
	 * @return
	 */
	public Matrix scalarMult(double x)
	{
		Matrix result = copy();
		
		if(getNNZ() == 0) // If for whatever reason this matrix is empty, don't bother doing anything.
			return null;
		
		// Loop over each row
		for(int i = 0; i < matrix.length; ++i)
		{
			List row = matrix[i];
			row.moveFront();
			
			// Over each column
			while(row.index() != -1)
			{
				Entry e = (Entry)row.get(); // Readability
				result.changeEntry(i + 1, e.getColData(), e.getVal() * x);
				row.moveNext();
			}
		}
		
		return result;
	}
	
	/**
	 * Returns a new Matrix that is the sum of this matrix with M
	 * Pre: getSize() == M.getSize()
	 * @param M
	 * @return
	 */
	public Matrix add(Matrix M)
	{
		if(getSize() != M.getSize())
			throw new RuntimeException("add(): getSize() != M.getSize()");
		if(this == M)
			M = M.copy(); // For A+A. Otherwise we operate too much on a single object
		
		Matrix result = new Matrix(getSize());
		
		// Matrix addition is A[ij] + B[ij]
		
		for(int i = 0; i < matrix.length; ++i)
		{
			List row = matrix[i];
			List rowM = M.matrix[i];
			List res = result.matrix[i];
			
			row.moveFront();
			rowM.moveFront();
			
			// While there is at least 1 row with a valid index
			while(!(row.index() == -1 && rowM.index() == -1))
			{
				// Figure out which row has the valid index
				// Both rows are valid
				if(row.index() != -1 && rowM.index() != -1)
				{
					// Find the smaller column, place that into res
					Entry e = (Entry)row.get();
					Entry eM = (Entry)rowM.get();
					// e is smaller than eM
					if(e.getColData() < eM.getColData())
					{
						// We're building each row from left to right, so always append because we're always moving forward
						res.append(new Entry(e.getColData(), e.getVal()));
						row.moveNext(); // Row is smaller, keep advancing until row == rowM, or we pass or fall off
					}
					else if(eM.getColData() < e.getColData())
					{
						res.append(new Entry(eM.getColData(), eM.getVal()));
						rowM.moveNext();
					}
					else // e.col == eM.col
					{
						// Now we actually add
						res.append(new Entry(e.getColData(), e.getVal() + eM.getVal()));
						// Advance both
						row.moveNext();
						rowM.moveNext();
					}
				}
				// Only row is valid
				else if(row.index() != -1 && rowM.index() == -1)
				{
					Entry e = (Entry)row.get();
					res.append(new Entry(e.getColData(), e.getVal()));
					row.moveNext();
				}
				// Only rowM is valid
				else
				{
					Entry eM = (Entry)rowM.get();
					res.append(new Entry(eM.getColData(), eM.getVal()));
					rowM.moveNext();
				}
			}
		}		
		return result;
	}
	
	/**
	 * Returns a new matrix that is the difference of this matrix with M
	 * Pre: getSize() == M.getSize()
	 * @param M
	 * @return
	 */
	public Matrix sub(Matrix M)
	{
		if(getSize() != M.getSize())
			throw new RuntimeException("sub(): getSize() != M.getSize()");
		if(this == M)
			M = M.copy(); // For A+A. Otherwise we operate too much on a single object
		
		Matrix result = new Matrix(getSize());
		
		// Matrix subtraction is A[ij] - B[ij]
		
		for(int i = 0; i < matrix.length; ++i)
		{
			List row = matrix[i];
			List rowM = M.matrix[i];
			List res = result.matrix[i];
			
			row.moveFront();
			rowM.moveFront();
			
			// While there is at least 1 row with a valid index
			while(!(row.index() == -1 && rowM.index() == -1))
			{
				//System.out.println(row.index() + ", " + rowM.index());
				// Figure out which row has the valid index
				// Both rows are valid
				if(row.index() != -1 && rowM.index() != -1)
				{
					// Find the smaller column, place that into res
					Entry e = (Entry)row.get();
					Entry eM = (Entry)rowM.get();
					// e is smaller than eM
					if(e.getColData() < eM.getColData())
					{
						// We're building each row from left to right, so always append because we're always moving forward
						res.append(new Entry(e.getColData(), e.getVal()));
						row.moveNext(); // Row is smaller, keep advancing until row == rowM, or we pass or fall off
					}
					else if(eM.getColData() < e.getColData())
					{
						// it's e - eM, so we need to preserve the negative
						res.append(new Entry(eM.getColData(), -1 * eM.getVal()));
						rowM.moveNext();
					}
					else // e.col == eM.col
					{
						// Now we actually subtract
						// If the result is 0, don't add it to the list
						if(e.getVal() - eM.getVal() != 0)
							res.append(new Entry(e.getColData(), e.getVal() - eM.getVal()));
						// Advance both
						row.moveNext();
						rowM.moveNext();
					}
				}
				// Only row is valid
				else if(row.index() != -1 && rowM.index() == -1)
				{
					Entry e = (Entry)row.get();
					res.append(new Entry(e.getColData(), e.getVal()));
					row.moveNext();
				}
				// Only rowM is valid
				else
				{
					Entry eM = (Entry)rowM.get();
					res.append(new Entry(eM.getColData(), -1 * eM.getVal()));
					rowM.moveNext();
				}
			}
		}		
		return result;
	}
	
	/**
	 * Returns a new matrix that is the transpose of this matrix
	 * @return
	 */
	public Matrix transpose()
	{
		Matrix result = new Matrix(getSize());
		
		for(int i = 0; i < matrix.length; ++i)
		{
			List row = matrix[i];
			row.moveFront();
	         
			while(row.index() >= 0) 
			{
				Entry e = (Entry)row.get();
				result.changeEntry(e.getColData(), i + 1, e.getVal());
				row.moveNext();
			}
		}
		return result;
	}
	
	/**
	 * Returns a new matrix that is the product of this matrix with M
	 * Pre: getSize() == M.getSize()
	 * @param M
	 * @return
	 */
	public Matrix mult(Matrix M)
	{
		if(getSize() != M.getSize())
			throw new RuntimeException("mult(): getSize() != M.getSize()");
		
		Matrix result = new Matrix(getSize());
		// this * M = this dot trans(M)
		Matrix mT = M.transpose();
		
		for(int i = 0; i < matrix.length; ++i)
		{
			// Don't do ANY calculations if there is nothing in the row. This slows things way down
			if(matrix[i].length() > 0)
			{
				List row = matrix[i];
				row.moveFront();
				
				for(int j = 0; j < mT.getSize(); ++j)
				{
					if(mT.matrix[j].length() > 0)
					{
						mT.matrix[j].moveFront();
						// Not val +=, but rather this is the jth col in the ith row
						result.changeEntry(i + 1, j + 1, dot(row, mT.matrix[j]));
						
					}
				}
			}
		}
		
		return result;
	}
	
	
	// Other functions
	
	@Override
	public String toString()
	{
		String result = "";
		
		for(int i = 0; i < matrix.length; ++i)
		{
			String s = matrix[i].toString();
			// Nested ternary to not display anything if the list output string is nothing.
			result += (!s.equals("") ? (i+1) + ": " + s + "\n" : "");
		}
		return result.trim();
	}
	
	/**
	 * Computes the vector dot product of the two matrix rows P, Q.
	 * @param P
	 * @param Q
	 * @return double
	 */
	private static double dot(List P, List Q)
	{
		double result = 0;
		Entry p, q;
		P.moveFront();
		Q.moveFront();
		
		// Using a for loop is not a good idea, since it's possible to move a slightly variable number of times
		while(P.index() > -1 && Q.index() > -1)
		{
			p = ((Entry)P.get());
			q = ((Entry)Q.get());
			
			// If the columns aren't the same, don't multiply them. The value is 0, so nothing is added
			if(p.getColData() == q.getColData())
			{
				result += p.getVal() * q.getVal();
				P.moveNext();
				Q.moveNext();
			}
			// If the col datas aren't the same, advance the one that is lower
			else if(p.getColData() > q.getColData())
			{
				Q.moveNext();
			}
			else
			{
				P.moveNext();
			}
		}
		
		return result;
	}
	
	
}