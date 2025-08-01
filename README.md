# Poker System MVP

A modular poker learning system built with a clean four-layer architecture, designed for studying Texas Hold'em strategy.

## Architecture

```
┌────────────┐
│   L5 展示  │  CLI Interface
└────┬───────┘
     │ ① User Intent (Pure Text/JSON)
┌────┴───────┐
│   L3 驱动  │  Game Loop Control
└────┬───────┘
     │ ② Sync Point (Translator Protocol)
┌────┴───────┐
│   L2 执行  │  PokerKit Executor (Thin Shell)
└────┬───────┘
     │ ③ Direct API Calls
┌────┴───────┐
│   L1 领域  │  Pure Rules + Immutable Data
└────────────┘
```

### Layer Responsibilities

- **L1 Domain**: Pure poker rules, zero third-party dependencies
- **L2 Executor**: Thin wrapper around PokerKit library
- **L3 Driver**: Game flow control and session management
- **L5 CLI**: User interface and interaction

### Clean Boundaries

- **① Pure text/JSON**: No embedded rules in UI layer
- **② Translator Protocol**: Single data conversion interface
- **③ Direct PokerKit calls**: No additional logic in executor

## Quick Start

1. **Install Dependencies**:
   ```bash
   cd poker_system/l2_executor
   pip install -r requirements.txt
   ```

2. **Run the Game**:
   ```bash
   cd poker_system
   python l5_cli/main.py --players 3 --sb 10 --bb 20 --stack 1000
   ```

3. **Game Commands**:
   - `f` or `fold` - Fold your hand
   - `c` or `call` - Call the current bet
   - `ch` or `check` - Check (when no bet to call)
   - `r <amount>` or `raise <amount>` - Raise by amount
   - `a` or `all-in` - Go all-in

## Example Game Session

```bash
$ python l5_cli/main.py --players 3 --sb 10 --bb 20 --stack 1000

Starting 3-player No-Limit Texas Hold'em
Blinds: $10/$20
Starting stacks: $1000

============================================================
STREET: PREFLOP
POT: $30
CURRENT BET: $20
============================================================
COMMUNITY CARDS: (none)

PLAYERS:
------------------------------------------------------------
  Player_0 (SB) [ACTIVE]
   Stack: $990 | Current Bet: $10 Cards: Ah Kd
  Player_1 (BB) [ACTIVE]
   Stack: $980 | Current Bet: $20
→ Player_2 (MP) [ACTIVE]
   Stack: $1000 | Current Bet: $0 Cards: Qh Js
------------------------------------------------------------

Player_2's turn. Legal actions: f, c, r <amount>, a
Available actions: f, c, r <amount>, a
Commands: f=fold, c=call, ch=check, r <amount>=raise, a=all-in
Player_2, enter your action: c
```

## Project Structure

```
poker_system/
├── l1_domain/               # Pure Rules (Zero Dependencies)
│   ├── game_state.py       # GameState, Player, Position classes
│   ├── action.py           # Action types and validation
│   └── translator.py       # Protocol definitions
├── l2_executor/             # PokerKit Integration
│   ├── pokerkit_executor.py # Translator implementation
│   └── requirements.txt    # pokerkit==0.6.3
├── l3_driver/               # Game Flow Control
│   └── game_loop.py        # Main game loop logic
└── l5_cli/                  # User Interface
    └── main.py             # CLI entry point
```

## Development Roadmap

### MVP ✅
- [x] 4-layer clean architecture
- [x] CLI interface
- [x] No-Limit Texas Hold'em
- [x] Single-hand gameplay
- [x] PokerKit integration

### v0.2 (Next)
- [ ] Multi-hand sessions
- [ ] Basic AI opponents
- [ ] Hand history export
- [ ] Statistics tracking

### v0.3 (Future)
- [ ] Web UI (FastAPI + WebSocket)
- [ ] Multi-player rooms
- [ ] Tournament mode

### v0.4 (Advanced)
- [ ] LLM-powered AI players
- [ ] Strategy analysis tools
- [ ] Learning recommendations

## Technical Notes

- **Language**: Python 3.9+
- **Core Engine**: PokerKit 0.6.3
- **Architecture Pattern**: Clean Architecture with Protocol-based boundaries
- **Testing**: Unit tests for each layer
- **Extensibility**: Plugin architecture for AI agents

## License

MIT License - See LICENSE file for details.