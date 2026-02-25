import express, { Request, Response } from 'express';
import cors from 'cors';
import { v4 as uuidv4 } from 'uuid';

// Types
interface Todo {
  id: string;
  title: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// In-memory storage (for demo purposes)
let todos: Todo[] = [];

// Health check endpoints
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage()
  });
});

app.get('/ready', (req: Request, res: Response) => {
  res.json({
    status: 'ready',
    timestamp: new Date().toISOString()
  });
});

// Get all todos
app.get('/api/todos', (req: Request, res: Response) => {
  res.json({
    success: true,
    count: todos.length,
    data: todos
  });
});

// Get single todo
app.get('/api/todos/:id', (req: Request, res: Response) => {
  const todo = todos.find(t => t.id === req.params.id);
  
  if (!todo) {
    return res.status(404).json({
      success: false,
      error: 'Todo not found'
    });
  }
  
  res.json({
    success: true,
    data: todo
  });
});

// Create new todo
app.post('/api/todos', (req: Request, res: Response) => {
  const { title } = req.body;
  
  if (!title || title.trim() === '') {
    return res.status(400).json({
      success: false,
      error: 'Title is required'
    });
  }
  
  const newTodo: Todo = {
    id: uuidv4(),
    title: title.trim(),
    completed: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  todos.push(newTodo);
  
  res.status(201).json({
    success: true,
    data: newTodo
  });
});

// Update todo
app.put('/api/todos/:id', (req: Request, res: Response) => {
  const todoIndex = todos.findIndex(t => t.id === req.params.id);
  
  if (todoIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Todo not found'
    });
  }
  
  const { title, completed } = req.body;
  
  if (title !== undefined) {
    todos[todoIndex].title = title.trim();
  }
  
  if (completed !== undefined) {
    todos[todoIndex].completed = completed;
  }
  
  todos[todoIndex].updatedAt = new Date().toISOString();
  
  res.json({
    success: true,
    data: todos[todoIndex]
  });
});

// Delete todo
app.delete('/api/todos/:id', (req: Request, res: Response) => {
  const todoIndex = todos.findIndex(t => t.id === req.params.id);
  
  if (todoIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Todo not found'
    });
  }
  
  const deletedTodo = todos.splice(todoIndex, 1)[0];
  
  res.json({
    success: true,
    data: deletedTodo
  });
});

// Delete all completed todos
app.delete('/api/todos/completed/all', (req: Request, res: Response) => {
  const completedTodos = todos.filter(t => t.completed);
  todos = todos.filter(t => !t.completed);
  
  res.json({
    success: true,
    count: completedTodos.length,
    data: completedTodos
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Backend server running on port ${PORT}`);
  console.log(`📝 Health check: http://localhost:${PORT}/health`);
  console.log(`📝 API: http://localhost:${PORT}/api/todos`);
});

export default app;
