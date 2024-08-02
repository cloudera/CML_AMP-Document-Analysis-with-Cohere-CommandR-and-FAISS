# Document Analysis with Cohere CommandR and FAISS

**Leverage Cohere's Command R model and FAISS Efficient Similarity Search for PDF Document Analysis**

![](/images/cohere-logo.png)

Cohere's Command R is a family of highly scalable language models that balance high performance with strong accuracy. Command-R is a large language model with open weights optimized for a variety of use cases including reasoning, summarization, and question answering. Command-R has the capability for multilingual generation evaluated in 10 languages and highly performant RAG capabilities.

This project automatically deploys an application, loads vectors into FAISS vector store, and allows for interfacing with Cohere's Command R Large Languge Model (LLM) within CML. The project is designed to be deployed as an AMP from the Cloudera AMP catalog.

![](/images/cohere-architecture.jpg)

## Cohere Chatbot

![](/images/chatbot.png)

## Model API Access
Navigate to https://dashboard.cohere.com/api-keys and access a Trial key free of charge, or for production usage, sign up for the Cohere Production API Key. Then save the API key for use when launching the AMP.

![](/images/cohere-api-keys.png)


## Storing PDF Files / Populate FAISS with Embeddings

### GUI
Storing PDFs in FAISS (local to the project file system) can be done via the web application as shown below, or by the Python job in the following section. For the GUI, file uploads are limited to 200MB and allow you to manually select a new index in FAISS with descriptions for better cataloging.

![](/images/upload-files.png)

### Automation with Python Job
Storing PDFs in the FAISS vector store done via the Python job need to have an index specified in the job. By default, we use "Default Index" and this can be changed by the user at any time. This job runs once as part of the AMP script to populate FAISS with sample docs. This (and any created index) may be removed via the UI if desired. It may also be used to add automation to the project for populating the vector store with new data on a schedule or periodically.

![](/images/upload-job.png)

## Project Requirements
#### CML Instance Types
- NO GPU required for this given it interfaces with Cohere via API
- A minimum 2 CPUs and 8GB RAM are required for the project to complete its AMP setup steps.

#### Recommended Runtime
JupyterLab - Python 3.11 - Standard - 2024.05

#### Resource Requirements
This AMP creates the following workloads with resource requirements:
- CML Session: `2 CPU, 8GB MEM`
- CML Jobs: `2 CPU, 8GB MEM`
- CML Application: `2 CPU, 8GB MEM`

#### External Resources
This AMP requires pip packages and models from Cohere. Depending on your CML networking setup, you may need to whitelist some domains:
- pypi.python.org
- pypi.org
- pythonhosted.org
- cohere.com
- dashboard.cohere.com
- coral.cohere.com

#### Security Boundaries
By default, the application, the project files, and the vector store are entitled to the single project owner deploying the project or an ML Admin. 

**1. Securing project resources**

CML applications are accessible by any user with read-only or higher permissions to the project. The creator of the application is responsible for managing the level of permissions the application users have on the project through the application. CML does not actively prevent you from running an application that allows a read-only user (i.e. Viewers) to modify files belonging to the project.

**2. Public Applications**
By default, authentication for applications is enforced on all ports and users cannot create public applications. If desired, the Admin user can allow users to create public applications that can be accessed by unauthenticated users.

To allow users to create public applications on an ML workspace:
As an Admin user, turn on the feature flag in Admin > Security by selecting Allow applications to be configured with unauthenticated access.
When creating a new application, select Enable Unauthenticated Access.
For an existing application, in Settings select Enable Unauthenticated Access.
To prevent all users from creating public applications, go to Admin > Security and deselect Allow applications to be configured with unauthenticated access. All existing public applications will immediately stop being publicly accessible.

**3. Transparent Authentication**
CML can pass user authentication to an Application, if the Application expects an authorized request. The REMOTE-USER field is used for this task.

Read more on security in CML Projects: [Securing Applications](https://docs.cloudera.com/machine-learning/cloud/applications/topics/ml-securing-applications.html)


## Technologies Used
#### Embedding and LLM Models
- [Cohere Command-R](https://docs.cohere.com/docs/command-r)
     - Large Language Model
- [Cohere embed-english-v3.0](https://docs.cohere.com/docs/cohere-embed)
     - Vector Embeddings Generation Model
#### Vector Store
- [FAISS](https://github.com/facebookresearch/faiss)
#### Chat Frontend
- [Streamlit](https://streamlit.io/)

## Deploying on CML
There are two ways to launch this prototype on CML:

1. **From Prototype Catalog** - Navigate to the Prototype Catalog on a CML workspace, select the "Cohere with PDFs Chatbot" tile, click "Launch as Project", click "Configure Project"

2. **As ML Prototype** - In a CML workspace, click "New Project", add a Project Name, select "ML Prototype" as the Initial Setup option, copy in the [repo URL](https://github.com/cloudera/CML_AMP-Cohere-Chatbot-with-PDFs), click "Create Project", click "Configure Project"

![](/images/amp-setup.png)

## Cohere Command R
Cohere Command R models are advanced natural language processing (NLP) models designed for high-performance text generation and understanding tasks. These models are part of Cohere's suite of NLP offerings and are optimized for rapid deployment and efficient execution. Command R models leverage state-of-the-art transformer architectures to provide robust capabilities in tasks such as text summarization, question answering, sentiment analysis, and more. They are designed to be easily integrated into various applications, offering scalability and flexibility for both small-scale and large-scale implementations. These models are particularly noted for their ability to handle complex language tasks with high accuracy and speed, making them suitable for enterprise-level applications and real-time processing needs.

## Cohere embed-english-v3.0
Cohere's embed-english-v3.0 model is a cutting-edge language model tailored for generating high-quality text embeddings from English language inputs. This model excels in capturing the semantic nuances of text, transforming them into dense vector representations that can be effectively utilized in various NLP tasks, including semantic search, text classification, and clustering. Leveraging advanced transformer architectures, embed-english-v3.0 ensures that the embeddings are both precise and efficient, making it a valuable tool for applications requiring deep text understanding. Its design facilitates seamless integration into existing systems, providing scalable and reliable performance for organizations aiming to enhance their natural language processing capabilities with robust embedding solutions.

## FAISS Efficient Similarity Search
FAISS (Facebook AI Similarity Search) is an open-source library developed by Facebook AI Research for efficient similarity search and clustering of dense vectors. It is optimized for searching through large datasets of vectors, such as those produced by machine learning models for tasks like image recognition, natural language processing, and recommendation systems. FAISS enables fast nearest neighbor search, leveraging algorithms and data structures designed for high-dimensional vector spaces. It supports a variety of indexing methods, including flat, inverted file, and hierarchical navigable small world graphs, to balance between speed and memory usage. FAISS is highly scalable, capable of handling billion-scale datasets, and is widely used in both academic research and industry applications for its speed and accuracy in vector search tasks.

## LangChain for Simplicity
LangChain is a powerful framework designed to simplify the development of applications powered by large language models (LLMs). It focuses on enabling seamless interaction with various language models, providing tools and abstractions for tasks such as prompt management, LLM chaining, data integration, and agent creation. LangChain allows developers to create complex applications by connecting multiple language model calls in a cohesive workflow, supporting both text-based and API-driven integrations. Its modular architecture supports various use cases, including conversational agents, data analysis, and automated content generation. LangChain is particularly valued for its flexibility and ease of use, making it an essential tool for developers looking to harness the full potential of LLMs in their applications.

## The Fine Print
IMPORTANT: Please read the following before proceeding. This AMP includes or otherwise depends on certain third party software packages. Information about such third party software packages are made available in the notice file associated with this AMP. By configuring and launching this AMP, you will cause such third party software packages to be downloaded and installed into your environment, in some instances, from third parties' websites. For each third party software package, please see the notice file and the applicable websites for more information, including the applicable license terms.

If you do not wish to download and install the third party software packages, do not configure, launch or otherwise use this AMP. By configuring, launching or otherwise using the AMP, you acknowledge the foregoing statement and agree that Cloudera is not responsible or liable in any way for the third party software packages.

Copyright (c) 2024 - Cloudera, Inc.
