# morons put commas in CSV fields!
s@,"\([^",]*\),\([^",]*\)",@,"\1 \2",@g
# morons put ampersands in fields destined for XML!
s@[&]@and@g
s@[/]@ or @g
s@  *@ @g
s@Manual Adjustments .* VAT@Manual Adjustments - VAT@