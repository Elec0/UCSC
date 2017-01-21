/*
 * Name: Aaron Steele, atsteele
 * Assignment: pa1
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

public class Lex 
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
			int n = lines.length;
			List l = new List();
			
			
			for(int i = 0; i < n; ++i)
			{
				
				// Use insertion sort method from front to back
				l.moveFront();
				
				while(l.index() >= 0)
				{
					// if next string comes after current
					if(lines[i].compareTo(lines[l.get()]) > 0)
					{
						l.moveNext();
					}
					else // if the next string comes before or is equal to string, place before
					{
						l.insertBefore(i);
						break;
					}
				}
				
				// If cursor falls off list, append to list
				if(l.index() < 0)
					l.append(i);
				
			}
			
			
			// Write to file
			BufferedWriter outputWriter = null;
			try
			{
				outputWriter = new BufferedWriter(new FileWriter(out));
				l.moveFront();
				while(l.index() >= 0)
				{
					outputWriter.write(lines[l.get()]);
					outputWriter.newLine();
					l.moveNext();
				}
				
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
		        out.add(line);
		    }
		} catch (IOException x) {
		    System.err.format("IOException: %s%n", x);
		}
		
		return out.toArray(new String[]{""});
	}
}