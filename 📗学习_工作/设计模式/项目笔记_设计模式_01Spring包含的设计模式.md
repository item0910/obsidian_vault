---
title: 项目笔记_设计模式_01Spring包含的设计模式
date: 2024-11-15
categories: IT项目
tags: 项目笔记/未完成项目/设计模式
author: 自己
mtime: 2024-11-15
---

### 1. **工厂模式（Factory Pattern）**

- **用途**：Spring IoC 容器使用工厂模式来创建和管理 Bean 的实例。
- **示例**：`BeanFactory` 和 `ApplicationContext` 都是 Spring 的核心工厂接口。通过配置文件或注解注册 Bean，容器负责实例化和注入依赖。

### 2. **单例模式（Singleton Pattern）**

- **用途**：在默认情况下，Spring 容器中定义的 Bean 是单例的，每次请求都返回同一个实例。
- **示例**：`@Scope("singleton")` 注解标识 Bean 的作用范围，确保全局单例。

### 3. **代理模式（Proxy Pattern）**

- **用途**：Spring AOP 通过代理模式来为目标对象添加横切关注点（如事务、日志、权限）。
- **示例**：`@Transactional`注解在方法上添加事务支持，实际是通过动态代理在方法执行前后管理事务。

### 4. **模板方法模式（Template Method Pattern）**

- **用途**：定义算法流程的框架，并将具体实现留给子类。Spring 中使用模板模式简化了各种重复性工作。
- **示例**：`JdbcTemplate`、`RestTemplate` 和 `JmsTemplate` 等，开发者只需关注业务逻辑，而不必重复实现通用操作。

### 5. **策略模式（Strategy Pattern）**

- **用途**：允许算法在运行时切换。Spring 中很多功能通过策略模式实现了可配置的行为。
- **示例**：Spring 的缓存机制中，`CacheManager`接口允许选择不同的缓存策略；事务管理中可以选择不同的事务策略。

### 6. **观察者模式（Observer Pattern）**

- **用途**：实现事件驱动模型，在事件发生时通知订阅者。
- **示例**：Spring 的事件模型使用观察者模式，通过`ApplicationEventPublisher`发布事件，`ApplicationListener`监听事件。

### 7. **装饰器模式（Decorator Pattern）**

- **用途**：在不修改原始对象的情况下扩展其功能。
- **示例**：Spring AOP 通过装饰器模式，在原方法执行前后添加增强功能（如日志、事务）。

### 8. **责任链模式（Chain of Responsibility Pattern）**

- **用途**：为请求创建一个处理链条，依次传递请求，直到被处理。
- **示例**：Spring Security 使用责任链模式处理请求，通过过滤器链实现一系列安全检查。

### 9. **适配器模式（Adapter Pattern）**

- **用途**：使接口不兼容的类可以一起工作。
- **示例**：Spring MVC 中的`HandlerAdapter` 允许不同类型的控制器（如 `Controller`、`HttpRequestHandler`）适配到统一的处理流程。

### 10. **桥接模式（Bridge Pattern）**

- **用途**：将抽象与实现分离，使它们可以独立变化。
- **示例**：Spring 中的消息系统、数据库访问等通过桥接模式连接到不同的实现，例如支持不同数据库或消息队列。
