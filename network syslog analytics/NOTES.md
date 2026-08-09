# Assessment notes

## Initial analysis of supplied Task 1 logs

The four supplied files contain **103 log events** in total.

Observed event types:

- Interface state changes and interface input errors
- BGP neighbor established/down events
- CPU threshold exceedance and recovery
- Thermal threshold exceedance and recovery
- SNMP authentication failures

The input syntax is consistent:

```text
timestamp device severity message
```

Examples of structured fields:

- `GigabitEthernet0/1` -> interface
- `10.10.10.2` -> BGP neighbor
- `10.0.2.55` -> SNMP source IP
- `90%` -> CPU numeric threshold

## Important interpretation

The supplied thermal lines say `sensor N exceeded threshold` but do not provide an actual temperature value. The parser therefore stores the sensor identifier as the numeric field for thermal events only as an implementation convenience; it should not be interpreted as degrees Celsius.

## Expected notable risks

The supplied data intentionally contains examples of:

- repeated interface flaps on R1/R2/R3
- short-lived BGP sessions
- repeated CPU spikes
- CPU >= 95% critical events
- repeated SNMP authentication failures from the same source
- thermal alarms with recovery messages
