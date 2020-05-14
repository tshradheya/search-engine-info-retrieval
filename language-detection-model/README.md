# N-Gram Language Detection Model 
[Description](https://www.comp.nus.edu.sg/~cs3245/hw1-lang.html)

Python Version 3.6 


## Running and Testing the Code

1. `python build_test_LM.py -b input.train.txt -t input.test.txt -o input.predict.txt`
   
2. `python eval.py input.predict.txt input.correct.txt`

This will print the accuracy for the test file inputs.

## General Overview

- The core part of the assignment is to build a language model based on given data based on certain heuristics.
  based on this given model, predict what language any input line/string belongs to based on probability
  from the language model.
- In the build_test_LM.py script, the function `build_LM()` will read data from training set and build a language model
  and maintain a vocabulary count for each language in order to easily find probability.
  Used a dictionary of dictionaries as it allows for easy query and is a pythonic data structure solution to the problem
  Some heuristics are used when building model which will be explained in detail in later parts
- In the `test_LM()` function, for each new test line, the language model previously build is used to predict the language
  by multiplying the probabilities (since the values tend to become 0 since they are so small, addition of logarithm was
  used instead.

## Algorithms and Steps

1. Read line from training data to build a language model. [Used some pre-processing of data based on config flags]
2. Create Language Model. [Used Add One smoothing and 4-gram character based ngrams]
3. Use Language model to predict language for the test data [Multiplication of probabilities used]
4. Write result into a file and then compare accuracy using eval.py
(More details can be found in comments in the code)

## Experiments and Analysis

Here I will discuss some design considerations and their analysis:

- Used START and END padding (< and >) because in these languages certain words will always be the starting ones and can
  be used to uniquely identify the language. Based on testing this seemed to be helpful and hence flag is turned on.
- For the given line, white spaces at start and end, end line character and periods at end were removed to sanitise and
  this helped useful as no improper model was build and padding already took care of period at the end.
  Moreover, all are converted to lowercase as upper case doesn't really help much with a certain language,
  and making all lowercase gives more advantages than disadvantages.
- Removing numbers: This was indeed useful as numbers don't belong to any language and not useful in helping us uniquely
 identifying a language
- Removing punctuations: Although this seemed a good idea in certain way and bad in other ways since some languages the
  punctuations are useful, I wanted to test this but due to limited knowledge of language and having already got 20/20
  accuracy without removing punctuations I decided to keep the flag off for removing punctuations as I couldn't prove it
  would be helpful
- Another test I did was to assign "other" language, if the
 (number of missing ngrams in line for the worse language/total ngrams) was greater than a threshold.
 The threshold was decided based on trial and error (0.85). However, the flag has been kept off as it gave 19/20
 accuracy. Although, I feel this can be useful for much bigger test data which has alien strings.
 Feel free to turn on the flag (SUPPORT_OTHER_LANGUAGE) in configuration if the test has results with "other" as predictions
- Other design considerations can be found in `ESSAY.txt`


### Files Details

- `build_test_LM.py`: Main file to be used to train and build model and then predict for test case.
                    Has 2 main functions to build and test. More details can be found in documentation present in code
- `README.txt`: Contains basic documentation for the Homework and the
              required details to run and test/grade the assignment. It's the file you are looking at right now
- `ESSAY.txt`: File containing succinct answers to some questions
