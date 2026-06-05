# DAS Hotkeys — In Progress

## System Design
- Daily stop: $250
- Grade allocations:
  - A+ = 80% = $200 (skipped for now — account too small)
  - A = 30% = $75
  - B = 15% = $37.50
  - C = 5% = $12.50
- Key logic: key number = stop distance in 10-cent increments (1 = 10c, 2 = 20c, etc.)
- Modifier: Shift = long entry, Ctrl = short entry
- Naming format: `Grade A - Long_10cent_stop_(750shares)`
- Account (live): U6846824
- Account (paper): TRIB11545

## Keyboard Layout
- `1234567890` = A+ row (skipped)
- `qwertyuiop` = A row ($75)
- `asdfghjkl;` = B row ($37.50)
- `zxcvbnm,./` = C row ($12.50)

---

## Grade A Row — Long (Shift + key) [$75 risk]

| Key | Name | Script |
|-----|------|--------|
| q | Grade A - Long_10cent_stop_(750shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=750;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-0.10 ACT:SELL STOPPRICE:AvgCost-0.10 QTY:750 TIF:DAY+;` |
| w | Grade A - Long_20cent_stop_(375shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=375;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-0.20 ACT:SELL STOPPRICE:AvgCost-0.20 QTY:375 TIF:DAY+;` |
| e | Grade A - Long_30cent_stop_(250shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=250;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-0.30 ACT:SELL STOPPRICE:AvgCost-0.30 QTY:250 TIF:DAY+;` |
| r | Grade A - Long_40cent_stop_(187shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=187;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-0.40 ACT:SELL STOPPRICE:AvgCost-0.40 QTY:187 TIF:DAY+;` |
| t | Grade A - Long_50cent_stop_(150shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=150;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-0.50 ACT:SELL STOPPRICE:AvgCost-0.50 QTY:150 TIF:DAY+;` |
| y | Grade A - Long_60cent_stop_(125shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=125;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-0.60 ACT:SELL STOPPRICE:AvgCost-0.60 QTY:125 TIF:DAY+;` |
| u | Grade A - Long_70cent_stop_(107shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=107;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-0.70 ACT:SELL STOPPRICE:AvgCost-0.70 QTY:107 TIF:DAY+;` |
| i | Grade A - Long_80cent_stop_(93shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=93;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-0.80 ACT:SELL STOPPRICE:AvgCost-0.80 QTY:93 TIF:DAY+;` |
| o | Grade A - Long_90cent_stop_(83shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=83;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-0.90 ACT:SELL STOPPRICE:AvgCost-0.90 QTY:83 TIF:DAY+;` |
| p | Grade A - Long_100cent_stop_(75shares) | `ROUTE=LIMIT;Price=Ask+0.05;Share=75;ACCOUNT=U6846824;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:AvgCost-1.00 ACT:SELL STOPPRICE:AvgCost-1.00 QTY:75 TIF:DAY+;` |

---

## TODO
- [ ] Grade A - Short row (Ctrl + qwertyuiop)
- [ ] Grade B - Long row (Shift + asdfghjkl;)
- [ ] Grade B - Short row (Ctrl + asdfghjkl;)
- [ ] Grade C - Long row (Shift + zxcvbnm,./)
- [ ] Grade C - Short row (Ctrl + zxcvbnm,./)
- [ ] Scale-out exit hotkeys (25%, 50%, flat)
- [ ] Confirm dash "-" works in DAS hotkey names
