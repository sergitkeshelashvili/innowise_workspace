-- 1) Standardize and aggregate the source data

WITH RECURSIVE
base_bom AS (
    SELECT
        plant_id,
        year,
        produced_material,
        component_material,
        SUM(component_material_quantity) as component_qty,
        MAX(component_material_release_type) as comp_release,
        MAX(component_material_production_type) as comp_prod_type,
        MAX(produced_material_release_type) as prod_release,
        MAX(produced_material_production_type) as prod_prod_type,
        MAX(produced_material_quantity) as prod_qty
    FROM bom_data
    GROUP BY plant_id, year, produced_material, component_material
),

-- 2) Recursive BoM Explosion: Start with materials where release_type = 'FIN'
bom_explosion AS (
    SELECT
        plant_id AS plant,
        year,
        produced_material AS fin_material_id,
        prod_release AS fin_material_release_type,
        prod_prod_type AS fin_material_production_type,
        prod_qty AS fin_production_quantity,
        produced_material AS prod_material_id,
        prod_release AS prod_material_release_type,
        prod_prod_type AS prod_material_production_type,
        prod_qty AS prod_material_production_quantity,
        component_material AS component_id,
        comp_release AS component_material_release_type,
        comp_prod_type AS component_material_production_type,
        component_qty AS component_consumption_quantity,
        1 AS depth
    FROM base_bom
    WHERE prod_release = 'FIN'
    -- 3) Recursive Join current components back to the base table to find their components
    UNION ALL
    SELECT
        be.plant,
        be.year,
        be.fin_material_id,
        be.fin_material_release_type,
        be.fin_material_production_type,
        be.fin_production_quantity,
        b.produced_material AS prod_material_id,
        b.prod_release AS prod_material_release_type,
        b.prod_prod_type AS prod_material_production_type,
        b.prod_qty AS prod_material_production_quantity,
        b.component_material AS component_id,
        b.comp_release AS component_material_release_type,
        b.comp_prod_type AS component_material_production_type,
        b.component_qty AS component_consumption_quantity,
        be.depth + 1
    FROM bom_explosion be
    INNER JOIN base_bom b ON be.component_id = b.produced_material
        AND be.year = b.year
        AND be.plant = b.plant_id
    WHERE be.component_material_release_type IN ('PROD', 'FIN')
      AND be.depth < 10
)

-- 4) Final Output Selection
SELECT
    plant,
    fin_material_id,
    fin_material_release_type,
    fin_material_production_type,
    fin_production_quantity,
    prod_material_id,
    prod_material_release_type,
    prod_material_production_type,
    prod_material_production_quantity,
    component_id,
    component_material_release_type,
    component_material_production_type,
    component_consumption_quantity,
    year
FROM bom_explosion
ORDER BY plant, year, fin_material_id, depth;
