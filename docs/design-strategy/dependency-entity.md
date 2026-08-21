# Entity一覧
- Preset
	- EquipmentEntity(あくまでも機器の設定であって個別を表さない)
	- EquipmentPortEntity(EquipmentEntityに複数持つことができる)
- Project
	- ProjectDataEntity
	- PerformanceDataEntity(コチラは日程ごとに保持する)
- LineGraph
	- Equipment(ライブで使われる個々の機器)
	- EquipmentPort



```mermaid
---
title: 回線関係のリレーション
---
erDiagram
    EquipmentEntity ||--o{ EquipmentPortEntity : "ポート"
    EquipmentEntity {
        id equip_id
        str name
        str node_type
        int quantity
    }
    EquipmentPortEntity {
        id port_id
        str name
        float pricePerUnit
    }
    Equipment ||--o{ EquipmentPort : "Portを参照"
    Equipment {
    id equip_node_id
    id performance
    }
    EquipmentPort {
	    id port_node_id
	    id equip_node_id
	    PortDirection direction
	    id equipment_id
    }
    EquipmentEntity ||--o{ Equipment : "参考にする"
    PerformaceEntity ||--o{ Equipment : "どの公演の話なのか"


```



# クラス実装
```mermaid
classDiagram
class TableEntity{
    +list[Colomn] columns
    -list[list[Any]] rows
    +data(row,column) Any
    +setData(row,column,context) bool
}

TableEntity <|-- EquipmentEntity
TableEntity <|-- EquipmentPortEntity

DataManger o-- EquipmentEntity
DataManger o-- EquipmentPortEntity
DataManger o-- AudioPatchSystem
AudioPatchSystem *-- Equipment
AudioPatchSystem *-- EquipmentPort
EquipmentEntity <-- Equipment
Equipment <--EquipmentPort
```



