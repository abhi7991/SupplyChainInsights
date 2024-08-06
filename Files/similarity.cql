CALL gds.graph.project('products', 
              ['Product','Country','Office','Vendor','Brand'], 
              {WEIGHT:{orientation:'REVERSE'},
              VENDOR:{},
              MANAGED_BY:{},
              BRAND:{orientation:'REVERSE'}}   
            );


MATCH (m:Product)
WHERE tolower(m.project_code) = '100-HT-T01'
WITH id(m) AS sourceNodeId
CALL gds.nodeSimilarity.filtered.stream('movies2',{
    nodeLabels:['Country','Office','Vendor','Brand'],
    relationshipTypes:['WEIGHT','VENDOR','MANAGED_BY','BRAND'],
    sourceNodeFilter: sourceNodeId,
    targetNodeFilter:'Product'
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
ORDER BY similarity DESCENDING, Entity1, Entity2            