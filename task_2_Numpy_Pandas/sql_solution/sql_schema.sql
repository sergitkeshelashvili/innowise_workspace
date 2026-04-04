CREATE TABLE bom_data (
    year INT,
    month INT,
    produced_material VARCHAR(50),
    produced_material_production_type VARCHAR(10),
    produced_material_release_type VARCHAR(10),
    produced_material_quantity NUMERIC(15, 2),
    component_material VARCHAR(50),
    component_material_production_type VARCHAR(10),
    component_material_release_type VARCHAR(10),
    component_material_quantity NUMERIC(15, 2),
    plant_id VARCHAR(20)
);

select * from bom_data;
