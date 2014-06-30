----------------------------- MODULE schematics -----------------------------
EXTENDS TLC

CONSTANTS
    InputSet, \* set of <<key, value>> tuples used for input
    InputMap, \* set of <<key, new_key>> tuples used to remap input keys
    AllowSet, \* set of keys to allow on output (whitelist)
    OutputMap \* set of <<key, new_key>> tuples used to remap output keys

\* OPERATORS

(* Map input keys to model fields and vice-versa *)
map_keys(keyval, mapping) ==
    IF \E t \in mapping : t[1] = keyval[1] THEN
        << (CHOOSE t \in mapping : t[1] = keyval[1])[2], keyval[2] >>
    ELSE keyval

ASSUME
    map_keys(<<"key", "val">>, {<<"key", "new_key">>}) = <<"new_key", "val">>

(* Field type functions (no-op) *)
StringType == [
    convert   |-> [value \in STRING |-> value],
    validate  |-> [value \in STRING |-> TRUE],
    primitive |-> [value \in STRING |-> value] ]
Field(x) == StringType

(* Convert values using field type *)
convert_values(keyval, function) ==
    << keyval[1], function[keyval[2]] >>

ASSUME
    convert_values(<<"key", "val">>, StringType.convert) = <<"key", "val">>

(* Validate values using field type *)
validate_values(keyval, function) ==
    function[keyval[2]]

ASSUME
    validate_values(<<"key", "val">>, StringType.validate) = TRUE

(* Filter fields for output *)
filter_keys(keyval, function, keyset) ==
    function[keyval[1], keyset]

whitelist == [key \in STRING, keyset \in SUBSET STRING |-> key \in keyset]

ASSUME
    filter_keys(<<"key", "val">>, whitelist, {"key2"}) = FALSE


(*--algorithm Schematics
variables
    MapSet = {<<>>}, ConvertSet = {<<>>}, ValidSet = {<<>>},
    FilterSet = {<<>>}, PrimitiveSet = {<<>>}, OutputSet = {<<>>}
begin
    \* Map input keys to model fields:
    MapSet := { map_keys(keyval, InputMap) : keyval \in InputSet };
    \* Convert values using field type:
    ConvertSet := { convert_values(<<key, val>>, Field(key).convert) : <<key, val>> \in MapSet };
    \* Validate values using field type:
    ValidSet := { <<key, val>> \in ConvertSet : validate_values(<<key, val>>, Field(key).validate) };
    \* Filter fields for output:
    FilterSet := { keyval \in ValidSet : filter_keys(keyval, whitelist, AllowSet) };
    \* Convert values to primitive type:
    PrimitiveSet := { convert_values(<<key, val>>, Field(key).primitive) : <<key, val>> \in FilterSet };
    \* Map model fields to output fields:
    OutputSet := { map_keys(keyval, OutputMap) : keyval \in FilterSet };
    assert \A <<key, val>> \in PrimitiveSet : key \in AllowSet;
    print OutputSet;
end algorithm*)

\* BEGIN TRANSLATION
VARIABLES MapSet, ConvertSet, ValidSet, FilterSet, PrimitiveSet, OutputSet, 
          pc

vars == << MapSet, ConvertSet, ValidSet, FilterSet, PrimitiveSet, OutputSet, 
           pc >>

Init == (* Global variables *)
        /\ MapSet = {<<>>}
        /\ ConvertSet = {<<>>}
        /\ ValidSet = {<<>>}
        /\ FilterSet = {<<>>}
        /\ PrimitiveSet = {<<>>}
        /\ OutputSet = {<<>>}
        /\ pc = "Lbl_1"

Lbl_1 == /\ pc = "Lbl_1"
         /\ MapSet' = { map_keys(keyval, InputMap) : keyval \in InputSet }
         /\ ConvertSet' = { convert_values(<<key, val>>, Field(key).convert) : <<key, val>> \in MapSet' }
         /\ ValidSet' = { <<key, val>> \in ConvertSet' : validate_values(<<key, val>>, Field(key).validate) }
         /\ FilterSet' = { keyval \in ValidSet' : filter_keys(keyval, whitelist, AllowSet) }
         /\ PrimitiveSet' = { convert_values(<<key, val>>, Field(key).primitive) : <<key, val>> \in FilterSet' }
         /\ OutputSet' = { map_keys(keyval, OutputMap) : keyval \in FilterSet' }
         /\ Assert(\A <<key, val>> \in PrimitiveSet' : key \in AllowSet, 
                   "Failure of assertion at line 69, column 5.")
         /\ PrintT(OutputSet')
         /\ pc' = "Done"

Next == Lbl_1
           \/ (* Disjunct to prevent deadlock on termination *)
              (pc = "Done" /\ UNCHANGED vars)

Spec == Init /\ [][Next]_vars

Termination == <>(pc = "Done")

\* END TRANSLATION

=============================================================================
\* Modification History
\* Last modified Mon Jun 30 17:12:56 GMT-03:00 2014 by paul
\* Created Wed Jun 25 17:29:13 GMT-03:00 2014 by paul
