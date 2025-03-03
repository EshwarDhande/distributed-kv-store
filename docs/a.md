### **Summary: Strong vs. Eventual Consistency & Replication in a Distributed Key-Value Store**  

#### **Strong vs. Eventual Consistency**  
- **Strong consistency** ensures that all nodes always return the latest committed value, requiring synchronization before responding. It is ideal for critical applications but comes with higher latency and lower availability.  
- **Eventual consistency** allows fast writes by updating replicas asynchronously, meaning reads may return stale data temporarily. It is well-suited for large-scale, highly available systems.  

#### **Consistency in Our Key-Value Store**  
- If **writes are synchronous** (ensuring all replicas update before acknowledging), the system follows **strong consistency**.  
- If **writes are asynchronous** (allowing temporary inconsistencies), the system follows **eventual consistency**.  
- The current replication strategy suggests **eventual consistency** since updates propagate asynchronously across nodes.  

#### **Replication Manager Overview**  
- **Manages peer servers**, maintains gRPC connections, and handles **PUT/DELETE replication**.  
- Uses **parallel execution** to replicate operations across nodes efficiently.  
- Implements **retry mechanisms** with exponential backoff for fault tolerance.  
- Runs asynchronously to **prevent blocking client operations** while ensuring data consistency.  

### **Key Takeaways**  
- The **ReplicationManager** ensures that all replicas stay updated, improving data durability.  
- The system prioritizes **high availability and scalability**, even if some nodes are temporarily out of sync.  
- Whether the system follows **strong or eventual consistency** depends on whether writes are confirmed across all replicas before acknowledging clients.