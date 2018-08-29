# PyCodeComplete
Python code predictions using a Recurrent Neural Network
##

## Motivation
Programmers spend a considerable amount of time fixing errors due to typos, retyping the same lines of code of a
common task, or typing boilerplate code. PyCodeComplete increases a programmer's productivity by provding auto-complete
suggestions to reduce the number of typos and the amount of repetitve typing.

## Product
The user interface for PyCodeComplete allows a programmer to start typing Python code and receive immediate auto-complete
suggestions that the programmer can then implement in his or her project. By using the auto-complete suggestions the
user can save time and avoid errors.

The code suggestions are provided by a Recurrent Nerual Network (RNN) that was trained on 1000 Python projects taken from
GitHub. 

## Gathering and Cleaning Data

Using the [GitHub GraphQL API v4](https://developer.github.com/v4/) I performed query to search for Python repositiories.
To ensure that only high quality Python code is used to train the RNN, I limited the seach to repositioreies with over
1000 stars. The query results are an stored on Amazon Aurora Relational Database with the following columns:

* Repository Name
* Owner
* Name With Owner
* Disk Usage
* Project's Url,
* SSH Url,
* Fork Count
* Star Count
* Watcher Count

After the repository metadata is collected I use [GitPython](https://github.com/gitpython-developers/GitPython) to clone
the repository to an Amazon AWS EC2 instance. Non-Python files are deleted to save space, since the RNN is only trained on
and predicts Python code.

I collected 2.4Gb of data totaling 5000 .py files with 10000 lines of code

## Data Preparation
The RNN is trained on a sequence of 100 characters. Training was performed on an [g2.8xlarge AWS EC2 instance](https://aws.amazon.com/ec2/instance-types/),
with 4 NVIDIA GRID K520 GPUs. This allowed me to train the RNN on batches of 512 of these sequences at a time.

During training, batches are generated as follows:

1. Read the next .py file
2. Encode the each character as a one-hot encoded vector of length 100, since I limited the allowable charcters to 
   python's strings.printable list of 100 characters. For example, the character 'a' is encoded as a 100 dimensional vector
   with all 0's with the exception of the 11th component which is 1.
3. 100 characters are assembled into a numpy array, resulting in a feature matrix of shape 100 x 100.
4. The target for this 100 x 100 feature matrix is the encoded 101st character
5. Because of memory limitations. A batch of 512 sequences and targets are prepared for each epoch.

## Modeling


## References