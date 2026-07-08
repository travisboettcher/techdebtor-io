---
title: "Rust and RISC-V Ramblings"
date: 2023-10-10
tags: ["Rust"]
---

I started my programming career with pretty run-of-the-mill programming languages - C++, Java, Python. Then, one of my professors had a challenge for the class: complete the assignment in Haskell. I was curious, so I jumped in - and loved it! I hadn't realized there could be such a vastly different way of thinking about programming, and this set me on a path to continuously dabble in random languages.

I took a Coursera course on Scala, was introduced to Akka and the Actor Model through that. That lead me to Elixir and Erlang, which I really enjoyed. I'm still convinced Akka, Elixir, Erlang, and the Actor Model are some of the most solid ways to develop large, distributed software systems.

I've also dabbled in various JavaScript frameworks and JVM languages; Golang; and C#. Most recently, and the main focus of this article, I decided to check out Rust. I'd seen a lot of press on it and it's memory safety, and was curious what I could take from it.

### Enter RISC-V

The project I decided to use to play with Rust, and I cannot remember where this idea came from, was to build a RISC-V emulator. RISC-V is an open source instruction set architecture, so basically what I was setting myself up for was a deep dive into the 145 page specification at the same time as learning Rust. I'm not sure what I was thinking.

My lofty goal - build an emulator capable of running a light-weight Linux distro, enough to have a terminal that I could interact with.

Where I'm at after 2 years of intermittent development - I can parse enough assembly to add two numbers together.

Ok, as lame as that sounds at face value, I think it's still pretty cool. I'm able to take the following assembly

```Assembly
addi x1, x0, 3
addi x2, x0, 5
add x3, x1, x2
```

and parse that into machine code

```Machine
00000000001100000000000010010011
00000000010100000000000100010011
00000000001000001000000110110011
```

and finally, iterate over those instructions to produce results that are actually correct!

```
register | value
   x0    |   0
   x1    |   3
   x2    |   5
   x3    |   8
```

(for reference, `3 + 5 = 8`. that's what this does. not groundbreaking.)

In it's current state, the project is only a partial implementation of the RISC-V instruction set. Most instructions are represented and work in some capacity, but there are a few (`FENCE`, I'm looking at you!) that I need to work into the system. Additionally, there are some nuances and details I want to make sure I have ironed out - for example, some of the instruction formats are laid out unintuitively and I think I may have gotten them incorrect.

The next step I want to take is to find or write a "Hello, World"-type program, and run that through the emulator. By making the program slightly more complex, I'll be able to really stress my code - and hopefully make it that much better.

### Learnings

The biggest hurtle I had to get over with Rust was the ownership model - what code owns what memory, and what other code can reference it. I still don't think I'm 100% proficient in it, and mostly learning to use it has meant learning new design patterns.

For example, coming from Java and OO programming, I immediately try to tackle problems using "Gang of Four" design patterns. However, Rust isn't OO, and if you try to fit OO patterns on top of `structs` and `traits`, you quickly run into issues. Primarily, I ran into issues trying to pass references around or doing some dynamic, runtime behavior pattern.

That isn't to say those things aren't possible - just that I had to rethink how I was approaching problems. And I'm still learning! I'm sure I currently rely too heavily on `match` expressions to determine behavior - basically every part of the system that needs to make a decision uses `match`.

Another difference that took some getting used to was error handling - no `throws` statements! You can `panic!` if the exception is truly unrecoverable, but the standard paradigm is to return a `Result`. A result can be either `Ok` or `Err`, and you handle those explicitly. I really like this pattern because it forces you to think about the error case - what do you do when the program isn't able to open a file? Maybe you do just `panic!`, or maybe there is some alternative file or user intervention that makes the error recoverable.

If you're curious about the project, or just want to check out how awful my code is, check it out here: [https://github.com/travisboettcher/risc-v-emulator](https://github.com/travisboettcher/risc-v-emulator). It's nowhere near feature-complete, but it has definitely been a fun side project, and who knows - maybe in two more years, it will be able to do more than add numbers!
