# PyCodeComplete
Python code predictions using a Recurrent Neural Network

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

In total, I collected 2.4Gb of data totaling 185,580 .py files containing 400,383 lines, 1,337,590 words, 16,056,221 characters of code

## Data Preparation
The RNN is trained on a sequence of 100 characters. Training was performed on an [g2.8xlarge AWS EC2 instance](https://aws.amazon.com/ec2/instance-types/),
with 4 NVIDIA GRID K520 GPUs. This allowed me to train the RNN on batches of 512 of these sequences at a time.

During training, batches are generated as follows:

1. Read the next .py file from the collection of GitHub repositiories
2. Encode the each character as a one-hot encoded vector of length 100, since I limited the allowable charcters to 
   python's strings.printable list of 100 characters. For example, the character 'a' is encoded as a 100 dimensional vector
   with all 0's with the exception of the 11th component which is 1.
3. 100 characters are assembled into a numpy array, resulting in a feature matrix of shape 100 x 100.
4. The target for this 100 x 100 feature matrix is the encoded 101st character
5. Because of memory limitations. A batch of 512 sequences and targets are prepared for each epoch.

## Modeling

![RNN Architecture Image](./images/model.png "RNN Architecture")

## Usage

Clone this repository with the command
```
git clone https://github.com/kevinafrica/pycodecomplete.git
```
GitHub scr


## Future Work


## References

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<title>Bibliography</title>
</head>
<body>
<div class="csl-bib-body" style="line-height: 1.35; margin-left: 2em; text-indent:-2em;">
  <div class="csl-entry">Andrej. <i>Char-Rnn: Multi-Layer Recurrent Neural Networks (LSTM, GRU, RNN) for Character-Level Language Models in Torch</i>. Lua, 2018. <a href="https://github.com/karpathy/char-rnn">https://github.com/karpathy/char-rnn</a>.</div>
  <span class="Z3988" title="url_ver=Z39.88-2004&amp;ctx_ver=Z39.88-2004&amp;rfr_id=info%3Asid%2Fzotero.org%3A2&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Adc&amp;rft.type=computerProgram&amp;rft.title=char-rnn%3A%20Multi-layer%20Recurrent%20Neural%20Networks%20(LSTM%2C%20GRU%2C%20RNN)%20for%20character-level%20language%20models%20in%20Torch&amp;rft.identifier=https%3A%2F%2Fgithub.com%2Fkarpathy%2Fchar-rnn&amp;rft.aulast=Andrej&amp;rft.au=Andrej&amp;rft.date=2018-08-13"></span>
  <div class="csl-entry">Moses, Caleb. <i>Keras-Char-Rnn: A Keras Implementation of Andrej Karpathy’s Char-Rnn Model in Python. Based on Keras with the TensorFlow Backend</i>. Jupyter Notebook, 2018. <a href="https://github.com/mathematiguy/keras-char-rnn">https://github.com/mathematiguy/keras-char-rnn</a>.</div>
  <span class="Z3988" title="url_ver=Z39.88-2004&amp;ctx_ver=Z39.88-2004&amp;rfr_id=info%3Asid%2Fzotero.org%3A2&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Adc&amp;rft.type=computerProgram&amp;rft.title=keras-char-rnn%3A%20A%20Keras%20implementation%20of%20Andrej%20Karpathy's%20char-rnn%20model%20in%20Python.%20Based%20on%20Keras%20with%20the%20TensorFlow%20backend&amp;rft.rights=GPL-3.0&amp;rft.identifier=https%3A%2F%2Fgithub.com%2Fmathematiguy%2Fkeras-char-rnn&amp;rft.aufirst=Caleb&amp;rft.aulast=Moses&amp;rft.au=Caleb%20Moses&amp;rft.date=2018-08-10"></span>
  <div class="csl-entry">“Recurrent Neural Networks.” TensorFlow. Accessed August 14, 2018. <a href="https://www.tensorflow.org/versions/r1.2/tutorials/recurrent">https://www.tensorflow.org/versions/r1.2/tutorials/recurrent</a>.</div>
  <span class="Z3988" title="url_ver=Z39.88-2004&amp;ctx_ver=Z39.88-2004&amp;rfr_id=info%3Asid%2Fzotero.org%3A2&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Adc&amp;rft.type=webpage&amp;rft.title=Recurrent%20Neural%20Networks&amp;rft.identifier=https%3A%2F%2Fwww.tensorflow.org%2Fversions%2Fr1.2%2Ftutorials%2Frecurrent&amp;rft.language=en"></span>
  <div class="csl-entry">“The Unreasonable Effectiveness of Recurrent Neural Networks.” Accessed August 6, 2018. <a href="http://karpathy.github.io/2015/05/21/rnn-effectiveness/">http://karpathy.github.io/2015/05/21/rnn-effectiveness/</a>.</div>
  <span class="Z3988" title="url_ver=Z39.88-2004&amp;ctx_ver=Z39.88-2004&amp;rfr_id=info%3Asid%2Fzotero.org%3A2&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Adc&amp;rft.type=webpage&amp;rft.title=The%20Unreasonable%20Effectiveness%20of%20Recurrent%20Neural%20Networks&amp;rft.identifier=http%3A%2F%2Fkarpathy.github.io%2F2015%2F05%2F21%2Frnn-effectiveness%2F"></span>
  <div class="csl-entry">Valkov, Venelin. “Making a Predictive Keyboard Using Recurrent Neural Networks — TensorFlow for Hackers (Part V).” <i>Medium</i> (blog), May 25, 2017. <a href="https://medium.com/@curiousily/making-a-predictive-keyboard-using-recurrent-neural-networks-tensorflow-for-hackers-part-v-3f238d824218">https://medium.com/@curiousily/making-a-predictive-keyboard-using-recurrent-neural-networks-tensorflow-for-hackers-part-v-3f238d824218</a>.</div>
  <span class="Z3988" title="url_ver=Z39.88-2004&amp;ctx_ver=Z39.88-2004&amp;rfr_id=info%3Asid%2Fzotero.org%3A2&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Adc&amp;rft.type=blogPost&amp;rft.title=Making%20a%20Predictive%20Keyboard%20using%20Recurrent%20Neural%20Networks%20%E2%80%94%20TensorFlow%20for%20Hackers%20(Part%20V)&amp;rft.description=Can%20you%20predict%20what%20someone%20is%20typing%3F&amp;rft.identifier=https%3A%2F%2Fmedium.com%2F%40curiousily%2Fmaking-a-predictive-keyboard-using-recurrent-neural-networks-tensorflow-for-hackers-part-v-3f238d824218&amp;rft.aufirst=Venelin&amp;rft.aulast=Valkov&amp;rft.au=Venelin%20Valkov&amp;rft.date=2017-05-25"></span>
  <div class="csl-entry">Zhang, Eric. <i>Char-Rnn-Keras: Multi-Layer Recurrent Neural Networks for Training and Sampling from Texts</i>. Python, 2018. <a href="https://github.com/ekzhang/char-rnn-keras">https://github.com/ekzhang/char-rnn-keras</a>.</div>
  <span class="Z3988" title="url_ver=Z39.88-2004&amp;ctx_ver=Z39.88-2004&amp;rfr_id=info%3Asid%2Fzotero.org%3A2&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Adc&amp;rft.type=computerProgram&amp;rft.title=char-rnn-keras%3A%20Multi-layer%20recurrent%20neural%20networks%20for%20training%20and%20sampling%20from%20texts&amp;rft.identifier=https%3A%2F%2Fgithub.com%2Fekzhang%2Fchar-rnn-keras&amp;rft.aufirst=Eric&amp;rft.aulast=Zhang&amp;rft.au=Eric%20Zhang&amp;rft.date=2018-08-02"></span>
</div></body>
</html>

## License
MIT License

Copyright (c) 2018 Kevin Africa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
