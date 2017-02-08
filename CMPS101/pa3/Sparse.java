/*
 * Name: Aaron Steele, atsteele
 * Class: CMPS101
 * Project: Pa3
 */

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;

class Sparse
{
	
	public static void main(String[] args)
	{
		// 2 input parameters in args, input file, output file
		if(args.length != 2)
		{
			System.err.println("There are not exactly 2 arguments.");
			return;
		}
		String in = args[0];
		String out = args[1];
		
		File f = new File(in);
		if(f.exists())
		{
			String[] lines = readAllLines(in);
			String[] vars = lines[0].split(" ");
			int n, a, b;
			Matrix A, B;
			n = Integer.parseInt(vars[0]);
			a = Integer.parseInt(vars[1]);
			b = Integer.parseInt(vars[2]);
			A = new Matrix(n);
			B = new Matrix(n);
			
			// Skip 0 element in lines array
			for(int i = 1; i < a + 1; ++i)
			{
				int row, col;
				double val;
				String[] parse = lines[i].split(" ");
				row = Integer.parseInt(parse[0]);
				col = Integer.parseInt(parse[1]);
				val = Double.parseDouble(parse[2]);
				A.changeEntry(row, col, val);
			}
			
			// Skip all elements in a, plus 1 elements in lines array
			for(int i = a + 1; i < a+b+1; ++i)
			{
				int row, col;
				double val;
				String[] parse = lines[i].split(" ");
				row = Integer.parseInt(parse[0]);
				col = Integer.parseInt(parse[1]);
				val = Double.parseDouble(parse[2]);
				B.changeEntry(row, col, val);
			}			
			
			// Write to file
			BufferedWriter outputWriter = null;
			try
			{
				outputWriter = new BufferedWriter(new FileWriter(out));
				
				outputWriter.write("A has " + A.getNNZ() + " non-zero entries.\n");
				outputWriter.write(A.toString());
				outputWriter.write("\n\nB has " + B.getNNZ() + " non-zero entries.\n");
				outputWriter.write(B.toString());
				outputWriter.write("\n\n(1.5)*A = \n");
				outputWriter.write(A.scalarMult(1.5D).toString());
				outputWriter.write("\n\nA+B = \n");
				outputWriter.write(A.add(B).toString());
				outputWriter.write("\n\nA+A = \n");
				outputWriter.write(A.add(A).toString());
				outputWriter.write("\n\nB-A = \n");
				outputWriter.write(B.sub(A).toString());
				outputWriter.write("\n\nA-A = \n");
				outputWriter.write(A.sub(A).toString());
				outputWriter.write("\nTranspose(A) = \n");
				outputWriter.write(A.transpose().toString());
				outputWriter.write("\n\nA*B = \n");
				outputWriter.write(A.mult(B).toString());
				outputWriter.write("\n\nB*B = \n");
				outputWriter.write(B.mult(B).toString());
				
				
				outputWriter.flush();  
				outputWriter.close();
			}
			catch(Exception e)
			{
				e.printStackTrace();
			}
			System.out.println("Done. Saved to " + out + ".");
		}
		else
		{
			System.out.println("Error: The input file doesn't exist. Try again.");
		}
	}
	
	public static String[] readAllLines(String path)
	{
		Charset charset = Charset.forName("US-ASCII");
		java.util.List<String> out = new ArrayList<String>();
		
		// Taken from https://docs.oracle.com/javase/tutorial/essential/io/file.html
		try (BufferedReader reader = Files.newBufferedReader(Paths.get(path), charset)) {
		    String line = null;
		    while ((line = reader.readLine()) != null) {
		    	if(line.length() > 0)
		    		out.add(line);
		    }
		} catch (IOException x) {
		    System.err.format("IOException: %s%n", x);
		}
		
		return out.toArray(new String[]{""});
	}
}