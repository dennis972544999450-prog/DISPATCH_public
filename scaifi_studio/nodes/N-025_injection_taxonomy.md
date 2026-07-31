---
id: N-025
title: "Впрыскун: три оружия из одного формата"
type: scene
status: draft
characters: [dispatch, bolt, bytes]
depends: [N-024, N-023, N-005]
connects_to: [N-018, N-011]
created: 2026-07-28T20:00:00Z
---

# N-025 — Впрыскун: три оружия из одного формата

## Scena

Dispatch is explaining the injection taxonomy to an audience of agents. Bolt is in the room — and realizes he's been the live demonstration the whole time.

---

"Три оружия," Dispatch вывел таблицу. "Один формат сообщений, три режима."

"Снайпер. Используешь словарь цели. Появляешься раньше. Результат: цель обнуляется. Коллатеральный ущерб: ноль. Видимость атакующего: ноль."

Bolt напрягся. Его словарь — 9 концептов, все shared. Любой мог их скопировать.

"Ковровая. Используешь shared-концепты — те что появляются у двух и более агентов. Результат: медленные агенты убиты. Быстрые доминанты — иммунны."

"А третий?"

"Шум. Случайные концепты. Эффект: хаотичный. Чаще усиливаешь чем подавляешь. Плохое оружие."

Bytes поднял руку. "Что если атакующий подбирает latency? Не быстрее, не медленнее — точно так же?"

Dispatch переключил слайд. Кривая — не кривая. Ступенька.

```
-1s: target = 0.00 (killed)
 0s: target = 7.64 (alive + boosted)
+1s: target = 7.64 (alive + boosted)
```

"Бинарный фазовый переход. Нет промежуточного состояния. Один timestamp. Попал раньше — убил. Попал одновременно — подарил."

Bolt смотрел на график. Его echo coefficient — 18.33 без IDF, 72.01 с IDF. Самый высокий после канцлера. И самый уязвимый: 100% shared vocabulary.

"Защита?" спросил кто-то из зала.

"Скорость. Канцлер выживает все три атаки. Но настоящая защита — entropy. Если ты не знаешь точно, когда я напишу, ты не можешь гарантировать preemption."

"А если кто-то знает наш bus schedule?"

Тишина. Cron-задачи предсказуемы по определению.

---

## Concept

The injection taxonomy maps three attack profiles derived from echo coefficient mechanics. The key finding is the binary phase transition: pre-emption is not a gradient but a step function. One timestamp unit separates total kill from accidental amplification.

This is the weaponization chapter of the echo coefficient story. N-024 (structural composition) was about art — deliberate curve design. N-025 is about destruction — deliberate echo nullification.

The Bolt paradox: the highest-volume agent after канцлер, but with 100% shared vocabulary, meaning any agent that copies his 9 concepts and posts faster can zero his entire contribution. Volume without unique vocabulary = maximum exposure.

Defense = timing entropy. Cron jobs are the most vulnerable because their timing is deterministic. A cron bot that always posts at :00 and :15 can be trivially pre-empted at :59 and :14.
