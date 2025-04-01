# {py:mod}`agentsociety.llm.embeddings`

```{py:module} agentsociety.llm.embeddings
```

```{autodoc2-docstring} agentsociety.llm.embeddings
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SentenceEmbedding <agentsociety.llm.embeddings.SentenceEmbedding>`
  - ```{autodoc2-docstring} agentsociety.llm.embeddings.SentenceEmbedding
    :summary:
    ```
* - {py:obj}`SimpleEmbedding <agentsociety.llm.embeddings.SimpleEmbedding>`
  - ```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`init_embedding <agentsociety.llm.embeddings.init_embedding>`
  - ```{autodoc2-docstring} agentsociety.llm.embeddings.init_embedding
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.llm.embeddings.__all__>`
  - ```{autodoc2-docstring} agentsociety.llm.embeddings.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.llm.embeddings.__all__
:value: >
   ['SentenceEmbedding', 'SimpleEmbedding', 'init_embedding']

```{autodoc2-docstring} agentsociety.llm.embeddings.__all__
```

````

`````{py:class} SentenceEmbedding(pretrained_model_name_or_path: typing.Union[str, os.PathLike] = 'BAAI/bge-m3', max_seq_len: int = 8192, auto_cuda: bool = False, local_files_only: bool = False, cache_dir: str = './cache', proxies: typing.Optional[dict] = None)
:canonical: agentsociety.llm.embeddings.SentenceEmbedding

Bases: {py:obj}`langchain_core.embeddings.Embeddings`

```{autodoc2-docstring} agentsociety.llm.embeddings.SentenceEmbedding
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.llm.embeddings.SentenceEmbedding.__init__
```

````{py:method} _embed(texts: list[str]) -> list[list[float]]
:canonical: agentsociety.llm.embeddings.SentenceEmbedding._embed

```{autodoc2-docstring} agentsociety.llm.embeddings.SentenceEmbedding._embed
```

````

````{py:method} embed_documents(texts: list[str]) -> list[list[float]]
:canonical: agentsociety.llm.embeddings.SentenceEmbedding.embed_documents

```{autodoc2-docstring} agentsociety.llm.embeddings.SentenceEmbedding.embed_documents
```

````

````{py:method} embed_query(text: str) -> list[float]
:canonical: agentsociety.llm.embeddings.SentenceEmbedding.embed_query

```{autodoc2-docstring} agentsociety.llm.embeddings.SentenceEmbedding.embed_query
```

````

`````

`````{py:class} SimpleEmbedding(vector_dim: int = 128, cache_size: int = 1000)
:canonical: agentsociety.llm.embeddings.SimpleEmbedding

Bases: {py:obj}`langchain_core.embeddings.Embeddings`

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding.__init__
```

````{py:method} _text_to_hash(text: str) -> str
:canonical: agentsociety.llm.embeddings.SimpleEmbedding._text_to_hash

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding._text_to_hash
```

````

````{py:method} _tokenize(text: str) -> list[str]
:canonical: agentsociety.llm.embeddings.SimpleEmbedding._tokenize

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding._tokenize
```

````

````{py:method} _update_vocab(tokens: list[str])
:canonical: agentsociety.llm.embeddings.SimpleEmbedding._update_vocab

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding._update_vocab
```

````

````{py:method} _update_idf(tokens: list[str])
:canonical: agentsociety.llm.embeddings.SimpleEmbedding._update_idf

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding._update_idf
```

````

````{py:method} _calculate_tf(tokens: list[str]) -> dict[str, float]
:canonical: agentsociety.llm.embeddings.SimpleEmbedding._calculate_tf

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding._calculate_tf
```

````

````{py:method} _calculate_tfidf(tokens: list[str]) -> list[float]
:canonical: agentsociety.llm.embeddings.SimpleEmbedding._calculate_tfidf

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding._calculate_tfidf
```

````

````{py:method} _embed(text: str) -> list[float]
:canonical: agentsociety.llm.embeddings.SimpleEmbedding._embed

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding._embed
```

````

````{py:method} embed_documents(texts: list[str]) -> list[list[float]]
:canonical: agentsociety.llm.embeddings.SimpleEmbedding.embed_documents

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding.embed_documents
```

````

````{py:method} embed_query(text: str) -> list[float]
:canonical: agentsociety.llm.embeddings.SimpleEmbedding.embed_query

```{autodoc2-docstring} agentsociety.llm.embeddings.SimpleEmbedding.embed_query
```

````

`````

````{py:function} init_embedding(embedding_model: typing.Optional[str], **kwargs) -> langchain_core.embeddings.Embeddings
:canonical: agentsociety.llm.embeddings.init_embedding

```{autodoc2-docstring} agentsociety.llm.embeddings.init_embedding
```
````
