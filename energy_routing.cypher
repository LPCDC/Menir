// Energy-aware routing using GDS A*
CALL gds.graph.project(
  'energyGraph',
  'Node',
  {REL: {type: 'REL', properties: 'energyCost'}}
);

CALL gds.shortestPath.astar.stream('energyGraph', {
  sourceNode: $srcId, targetNode: $dstId,
  relationshipWeightProperty: 'energyCost'
})
YIELD totalCost, nodeIds
RETURN totalCost, nodeIds;
