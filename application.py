import torch
from transformers import pipeline
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
import os 
from flask import Flask, render_template, request, session, url_for

summarizer = pipeline("summarization")

application = Flask(__name__)

@application.route('/')
def index():
	return render_template('index.html')

def pdf2txt(inPDFfile, outTXTFile):
                inFile = open(inPDFfile, 'rb')
                resMgr = PDFResourceManager()
                retData = io.StringIO()
                TxtConverter = TextConverter(resMgr, retData, laparams=LAParams())
                interpreter = PDFPageInterpreter(resMgr, TxtConverter)
            
                #Process each page in pdf file
                for page in PDFPage.get_pages(inFile):
                    interpreter.process_page(page)
                    
                txt = retData.getvalue()
                
                #save output data to a txt file
                return txt

#text = ''  

@application.route('/summarizer', methods =["GET", "POST"])
def summary():
   myfile = request.files['myfile']
   
   myfile.save(myfile.filename)


   inPDFfile = myfile.filename   
   outTXTFile = 'file.txt'

   try:
      txt = pdf2txt(inPDFfile, outTXTFile)
      with open(outTXTFile, 'w') as f:
            f.write(txt)
   except Exception as e:
            print(e)

   with open('file.txt') as f:
      text = f.readlines() 

   #Combining the test into one long string
   ARTICLE = ' '.join(text)

   result = preprocessing(ARTICLE)

   #Saving summary into a txt file
   with open ('summary.txt', 'w') as f:

      for v in result:
         f.write(v['summary_text'])
         f.write('\n')

   return render_template("result.html", result = result) 

#Summarization
#This is to make text readable after splitting
def preprocessing(txt):
   #Combining the test into one long string
   #ARTICLE = ' '.join(text)
   ARTICLE = txt.replace('.', '.<eos>')
   ARTICLE = ARTICLE.replace('!', '!<eos>')
   ARTICLE = ARTICLE.replace('?', '?<eos>')

   #Splitting ARTICLE into individual sentences using <eos>
   sentences = ARTICLE.split('<eos>')

   #Dividing the text (sentences) into smaller chunks to allow all the text be passed in using small chunks
   max_chunk = 300
   current_chunk = 0
   chunks = []

   for sentence in sentences:
      if len(chunks) == current_chunk + 1:
         if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
               chunks[current_chunk].extend(sentence.split(' '))
         else:
               current_chunk += 1
               chunks.append(sentence.split(' '))
      else:
         print(current_chunk)
         chunks.append(sentence.split(' '))

   to_summarize = chunks[0:15]

   #Joining individual words together again to form sentences
   for chunk_id in range(len(to_summarize)):
      to_summarize[chunk_id] = ' '.join(to_summarize[chunk_id])

   #Passing the chunks to be summarized
   result = summarizer(to_summarize, max_length=150, min_length=30, do_sample=False)

   return result


if __name__ == "__main__":
    application.run()