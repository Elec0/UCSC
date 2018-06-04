import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class LogisticRegression_withBias {

    /** the learning rate */
    private double rate=0.01;

    /** the weights to learn */
    private double[] weights;

    /** the number of iterations */
    private int ITERATIONS = 200;

    /** Constructor initializes the weight vector. Initialize it by setting it to the 0 vector. **/
    public LogisticRegression_withBias(int n) { // n is the number of weights to be learned
		weights = new double[n]; // Add an extra 1 for the bias
    }

    /***
     * Implement the function that returns the L2 norm of the weight vector
     * The L2 norm is sqrt(x[i]^2)
     *
     * @return
     */
    private double weightsL2Norm() {
        double sum = 0;
        for(int i = 0; i < weights.length; ++i) {
            sum += Math.pow(weights[i], 2);
        }
        return Math.sqrt(sum);
    }

    /**
     * @param z = W0 + W1*Feat1 + W2*Feat2 [...]
     * @return The probability that z is of class 1
     */
    private static double sigmoid(double z) {
        // The standard sigmoid equation
        return 1.0/(1 + Math.exp(-z));
    }

    /** Takes a test instance as input and outputs the probability of the label being 1 **/
    /** This function should call sigmoid() **/
    private double probPred1(double[] x) {
        double z = 0;
        // Now calculate z for the sigmoid function
        // z = W0 + W1*Feat1 + W2*Feat2 [...]
        for(int i = 0; i < x.length; ++i) {
            z += weights[i] * x[i];
        }
        return sigmoid(z);
    }

    /** Takes a test instance as input and outputs the predicted label **/
    /** This function should call probPred1() **/
    public int predict(double[] x) {
        double prob = probPred1(x);

        // Predicted class = 1 iff Prob of predictec class >= 0.5
        if(prob >= 0.5)
            return 1;
        else
            return 0;
    }

	/** This function takes a test set as input, call the predict() to predict a label for it, and prints the accuracy, P, R, and F1 score
	 * 	of the positive class and negative class and the confusion matrix **/
	public void printPerformance(List<LRInstance> testInstances) {
		double acc = 0;
		double p_pos = 0, r_pos = 0, f_pos = 0;
		double p_neg = 0, r_neg = 0, f_neg = 0;
		int TP=0, TN=0, FP=0, FN=0; // TP = True Positives, TN = True Negatives, FP = False Positives, FN = False Negatives

		// Loop over all the instances
		for(LRInstance instance : testInstances) {
			// Get the predicted label
			int predLabel = predict(instance.x);

			if(predLabel == instance.label) {
				// If the prediction was correct, increment the True variables
				if(predLabel == 0)
					TN++;
				else
					TP++;
			}
			else {
				// If the prediction was incorrect, increment the False variables
				if(predLabel == 0)
					FN++;
				else
					FP++;
			}
		}

		// Calculate the accuracy from the number of correctly ID'd instances
		acc = (TP + TN) / (double)(TP + TN + FP + FN);

		// Calculate the precision and recall for the positive classes
		p_pos = TP / (double)(TP + FP);
		r_pos = TP / (double)(TP + FN);
		// Same but for negative classes
		p_neg = TN / (double)(TN + FN);
		r_neg = TN / (double)(TN + FP);


		// Calculate the F1 scores
		f_pos = 2 * ((p_pos * r_pos) / (p_pos + r_pos));
		f_neg = 2 * ((p_neg * r_neg) / (p_neg + r_neg));

		System.out.println("Accuracy="+acc);
		System.out.println("P, R, and F1 score of the positive class=" + p_pos + " " + r_pos + " " + f_pos);
		System.out.println("P, R, and F1 score of the negative class=" + p_neg + " " + r_neg + " " + f_neg);
		System.out.println("Confusion Matrix");
		System.out.println(TP + "\t" + FN);
		System.out.println(FP + "\t" + TN);
	}


    /** Train the Logistic Regression using Stochastic Gradient Ascent **/
    /** Also compute the log-likelihood of the data in this function **/
    public void train(List<LRInstance> instances) {
        int instLabelSum = 0;
        for(LRInstance inst : instances) {
            instLabelSum += inst.label;
        }

        for (int n = 0; n < ITERATIONS; n++) {
            double lik = 0.0; // Stores log-likelihood of the training data for this iteration
            for (int i=0; i < instances.size(); i++) {
                // Train the data
                // Use gradient ascent to maximize the log likelihood
                double[] curX = instances.get(i).x;
                double predErr =  instances.get(i).label - probPred1(instances.get(i).x);

                // Loop through the features
                for(int k = 0; k < weights.length; ++k) {
                    // Update the weights according to the gradient ascent formula
                    weights[k] = weights[k] + rate * curX[k] * predErr;
                }

                // Compute the log-likelihood of the data here. Remember to take logs when necessary
                // Calculate the sum of weights * features that we need twice ahead of time
                double weightedSum = 0;
                for(int k = 0; k < weights.length; ++k) {
                    weightedSum += weights[k] * curX[k];
                }
                lik = instLabelSum * weightedSum - Math.log(1 + Math.exp(weightedSum));
            }
            System.out.println("iteration: " + n + " lik: " + lik);
        }
    }

    public static class LRInstance {
        public int label; // Label of the instance. Can be 0 or 1
        public double[] x; // The feature vector for the instance

        public LRInstance(int label, double[] x) {
            this.label = label;
            this.x = new double[x.length+1]; // Add a new spot for the bais
            System.arraycopy(x, 0, this.x, 0, x.length);
            // Set the new spot to always be 1
            this.x[this.x.length-1] = 1;
        }
    }

    /** Function to read the input dataset **/
    public static List<LRInstance> readDataSet(String file) throws FileNotFoundException {
        List<LRInstance> dataset = new ArrayList<LRInstance>();
        Scanner scanner = null;
        try {
            scanner = new Scanner(new File(file));

            while(scanner.hasNextLine()) {
                String line = scanner.nextLine();
                if (line.startsWith("...")) { // Ignore the header line
                    continue;
                }
                String[] columns = line.replace("\n", "").split(",");

                // every line in the input file represents an instance-label pair
                int i = 0;
                double[] data = new double[columns.length - 1];
                for (i=0; i < columns.length - 1; i++) {
                    data[i] = Double.valueOf(columns[i]);
                }
                int label = Integer.parseInt(columns[i]); // last column is the label
                LRInstance instance = new LRInstance(label, data); // create the instance
                dataset.add(instance); // add instance to the corpus
            }
        } finally {
            if (scanner != null)
                scanner.close();
        }
        return dataset;
    }


    public static void main(String... args) throws FileNotFoundException {
        List<LRInstance> trainInstances = readDataSet("HW3_TianyiLuo_train.csv");
        List<LRInstance> testInstances = readDataSet("HW3_TianyiLuo_test.csv");

        // create an instance of the classifier
        int d = trainInstances.get(0).x.length;
        LogisticRegression_withBias logistic = new LogisticRegression_withBias(d);

        logistic.train(trainInstances);

        System.out.println("Norm of the learned weights = "+logistic.weightsL2Norm());
        System.out.println("Length of the weight vector = "+logistic.weights.length);

        // printing accuracy for different values of lambda
        System.out.println("-----------------Printing train set performance-----------------");
        logistic.printPerformance(trainInstances);

        System.out.println("-----------------Printing test set performance-----------------");
        logistic.printPerformance(testInstances);
    }

}

