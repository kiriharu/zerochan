# Zerochan

Library for Zerochan.net with pics parsing and downloader included!

## Features
* CLI utility for pics downloading from zerochan.net
* Library for create custom downloader (you can write own) or data analyze.
* Strong typed!

## Installation:

### Using pip
`pip install zerochan`
### Using poetry
`poetry add zerochan`

## Using as library: 

First, you should create `Zerochan` instance:
```python
from zerochan import ZeroChan

zerochan_instance = ZeroChan()
```

Now, you can set some args for request

```python
from zerochan import ZeroChan, PictureSize, SortBy

zerochan = ZeroChan()

zerochan.search("Spain")  # Set title to search
zerochan.size(PictureSize.BIGGER_AND_BETTER) # Set quality and pic size
zerochan.sort(SortBy.POPULAR) # Set sorting (now only popular)
zerochan.page(1) # Page to parse
zerochan.authorize("hjsaf7afkjsaf78", "127364") # Authorize by z_hash and z_id in cookies
```

...or set args like this:

```python
zerochan.search("Spain")\
    .size(PictureSize.BIGGER_AND_BETTER)\
    .sort(SortBy.POPULAR)
```

After all settings, you should call `.pics()` to get pics:

```python
data = zerochan.pics()
for img in data.images:
    print(img.url)
```