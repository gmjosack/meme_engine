# meme_engine

## Description
Meme Generator for AppEngine

This is a small project to allow you to throw up a quick
internal meme generator on AppEngine for internal use at
your company.

It's still very much a work in progress.

## Building

This project uses bower to pull in it's third-party dependencies
so after cloning and `cd`ing into the base directory run

```bash
bower install
```

## Development

There is an `example-app.yaml` that you should `cp` to `app.yaml`
and you should replace the `application:` value to the name of
your application. Once that is done you can run

```bash
dev_appserver.py --log_level=debug
```

## Uploading to AppEngine

```bash

appcfg.py update

```

## TODO

 * Sorting
 * Search
 * User Pages (show memes from that user)
 * Show Memes created with a template on template page
 * Error Handling on Add Template Page
 * Lots of memcache
 * Animated GIF support
